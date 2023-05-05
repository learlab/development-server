from kubespawner.utils import get_k8s_model
from kubernetes_asyncio.client.models import ( V1Volume, V1VolumeMount )

naep_competition = {
  'name': 'naep-competition',
  'pvc': 'naep-competition-storage-claim',
  'mountPath': '/home/jovyan/naep-competition',
  'readOnly': False
}

user_volume_map = {
  'langdon-holmes': [naep_competition],
  'scott-crossley': [naep_competition],
  'wesley-morris': [naep_competition]
}

def modify_pod_hook(spawner, pod):
    try:
        user = spawner.user.name
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
