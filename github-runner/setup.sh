#!/usr/bin/env bash
# Install the self-hosted GitHub Actions runner that deploys learlab/itell-api
# (learlab/itell-api#200). Run on the lab server as root:
#
#   sudo ./setup.sh <registration-token>
#
# The token comes from itell-api -> Settings -> Actions -> Runners -> New
# self-hosted runner, or from
#   gh api -X POST repos/learlab/itell-api/actions/runners/registration-token --jq .token
# It expires after an hour. Never commit it: this repository is public.
#
# Safe to re-run; it replaces an existing registration of the same name.
set -euo pipefail

token=${1:?usage: sudo ./setup.sh <registration-token>}

repo_url=https://github.com/learlab/itell-api
runner_user=itell-ci
runner_name=lab-server
runner_dir=/opt/actions-runner/itell-api
env_dir=/srv/itell-api

version=2.338.2
sha256=baebf204307bac6193480852732f0aba2ae97b6c5597c244f4d5558390147c40
tarball=actions-runner-linux-x64-$version.tar.gz

[ "$(id -u)" -eq 0 ] || { echo "Run as root (sudo)." >&2; exit 1; }

# A local system user. docker and microk8s are what `make staging` and
# `make deploy` need; both are root-equivalent on this host. users can read the
# itell-api env files.
if ! id "$runner_user" > /dev/null 2>&1; then
	useradd --system --create-home --home-dir "/var/lib/$runner_user" \
		--shell /bin/bash "$runner_user"
fi
usermod -aG docker,microk8s,users "$runner_user"

# The env files hold production keys. Group users only, nobody else.
chgrp users "$env_dir/.env" "$env_dir/.env.staging"
chmod o-rwx "$env_dir/.env" "$env_dir/.env.staging"
chmod g+r "$env_dir/.env" "$env_dir/.env.staging"

mkdir -p "$runner_dir"
chown "$runner_user": "$runner_dir"
cd "$runner_dir"

if [ ! -x ./config.sh ]; then
	curl -fsSL -o "$tarball" \
		"https://github.com/actions/runner/releases/download/v$version/$tarball"
	echo "$sha256  $tarball" | sha256sum -c -
	sudo -u "$runner_user" tar xzf "$tarball"
	rm "$tarball"
	./bin/installdependencies.sh
fi

# Re-running: stop the service and drop the local registration. config.sh
# refuses to configure over it, and --replace takes over the old registration
# on GitHub's side.
if [ -f .service ]; then
	./svc.sh stop || true
	./svc.sh uninstall || true
fi
rm -f .runner .credentials .credentials_rsaparams

# Registered on itell-api only, never the learlab org: an org runner can be
# targeted from any learlab repo, public ones included.
sudo -u "$runner_user" ./config.sh --unattended --replace \
	--url "$repo_url" --token "$token" \
	--name "$runner_name" --labels "$runner_name" --work _work

./svc.sh install "$runner_user"
./svc.sh start

# make push needs DockerHub. Log in once with an access token for
# langdonholmes (hub.docker.com -> Account settings -> Personal access tokens,
# Read & Write).
if ! sudo -u "$runner_user" -H test -f "/var/lib/$runner_user/.docker/config.json"; then
	echo
	echo "Log the runner in to DockerHub (username langdonholmes, an access token as the password):"
	sudo -u "$runner_user" -H docker login -u langdonholmes
fi

echo
echo "Runner '$runner_name' is installed. Check it under $repo_url/settings/actions/runners"
