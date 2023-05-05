from dockerspawner import DockerSpawner

class PrivateStorageSpawner(DockerSpawner):
    extra_volume_map = {
        'langdon-holmes': ['naep-competition'],
        'scott-crossley': ['naep-competition'],
        'wesley-morris': ['naep-competition']
    }

    def start(self):
        # username is self.user.name
        if self.user.name in extra_volume_map:
            volumes = extra_volume_map[self.user.name]
            # add team volume to volumes
            for volume in volumes:
               self.volumes[volume] = '/home/{}'.format(volume)
        return super().start()

c.JupyterHub.spawner_class = PrivateStorageSpawner
