from kubernetes import client
from kubespawner.utils import get_k8s_model
from kubernetes.client.models import ( V1Volume, V1VolumeMount )

naep-competition = {
  'name': 'naep-competition',
  'pvc': 'naep-competition-storage-claim',
  'mountPath': '/home/jovyan/naep-competition',
  'readOnly': False
}

user_volume_map = {
  'langdon-holmes': [naep-competition],
  'scott-crossley': [naep-competition],
  'wesley-morris': [naep-competition]
}

def modify_pod_hook(spawner, pod):
    try:
        user = spawner.user.name
        spawner.log.info("User name is: " + str(user))
        if user in user_volume_map:
            for volume in user_volume_map[user]:
                pod.spec.volumes.append(
                    get_k8s_model(V1Volume, {
                        'name' : volume['name'],
                        'persistentVolumeClaim': {
                            'claimName': volume['pvc']
                        }
                    })
                )

                # Note implicitly only 1 container...
                pod.spec.containers[0].volume_mounts.append(
                    get_k8s_model(V1VolumeMount, {
                        'name' : volume['name'],
                        'mountPath' : volume['mountPath'],
                        'readOnly': volume['readOnly']
                    })
                )
    except Exception as e:
        spawner.log.info("Exception in shared-mounts" + str(e))
        pass
    return pod

c.KubeSpawner.modify_pod_hook = modify_pod_hook
