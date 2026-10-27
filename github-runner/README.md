# GitHub Actions runner for itell-api

A self-hosted [GitHub Actions runner](https://github.com/actions/runner) on the
lab server. It runs the [itell-api](https://github.com/learlab/itell-api)
deploy workflows (learlab/itell-api#200):

- **Deploy to staging**: every push to `main` builds the image, runs the tests on
  CPU, pushes it to DockerHub and deploys it to the staging API.
- **Promote to production**: started by hand in the Actions tab. Deploys an image
  that is already on staging to production.

The workflows call the itell-api `Makefile`, the same targets you would run by
hand. See "Deployment" in the itell-api README.

## How it works

The runner is GitHub's program, installed in `/opt/actions-runner/itell-api` and
run by systemd as the `itell-ci` user
(`actions.runner.learlab-itell-api.lab-server.service`). It keeps an outbound
HTTPS connection to github.com and waits for jobs labeled `lab-server`. It opens
no ports. Jobs run directly on the host (not in a container), one at a time, in
their own checkout under `_work/`.

`itell-ci` is in these groups:

- `docker` and `microk8s`, to build images and deploy. Both are root-equivalent
  on this host, so anyone who can push to itell-api's `main` can run code here as
  root. itell-api is private, so that is the lab's itell-api collaborators.
- `users`, to read `/srv/itell-api/.env` and `.env.staging`. Those files stay on
  this server and are the only copy; GitHub never sees them.

Its DockerHub login (for `docker push`) is in `/var/lib/itell-ci/.docker/`.

The runner is registered on itell-api only, not the learlab organization. An
organization runner could be targeted from any learlab repo, including public
ones, where a pull request from anyone would run code on this server.

## Install or re-register

```bash
token=$(gh api -X POST repos/learlab/itell-api/actions/runners/registration-token --jq .token)
sudo ./setup.sh "$token"
```

The token needs admin access to itell-api and expires after an hour. Do not
commit it; this repository is public. The script is safe to re-run.

## Operate

```bash
sudo systemctl status actions.runner.learlab-itell-api.lab-server
journalctl -u actions.runner.learlab-itell-api.lab-server -f
```

The runner updates itself. To remove it:

```bash
cd /opt/actions-runner/itell-api
sudo ./svc.sh stop && sudo ./svc.sh uninstall
token=$(gh api -X POST repos/learlab/itell-api/actions/runners/remove-token --jq .token)
sudo -u itell-ci ./config.sh remove --token "$token"
```
