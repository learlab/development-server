# To adjust the spawn options presented to the user, we must create a custom
# options_form function, and this example demonstrates how!
#
#
#
# profile_list (KubeSpawner class) can be configured as a convenience to
# generate set HTML for the options_form configuration (Spawner class).
#
# If options_form is set (or indirectly set through profile_list), it is the
# HTML that users are presented with when users have signed in and want to start
# a server.
#
# While options_form is allowed to be a HTML string, it can also be a callable
# function, that when called generates HTML. If a callable function return a
# falsy value, no form will be rendered.
#
# In this custom options_form function, we will make a decision based on user
# information, update profile_list, and rely on the profile_list logic to render
# the HTML for us.
#
async def custom_options_form(spawner):
    # See the pre_spawn_hook example for more ways to get information about the
    # user
    auth_state = await spawner.user.get_auth_state()
    user_details = auth_state["oauth_user"]
    gpu_access = user_details.get("gpu_access", False)

    # Declare the common profile list for all users
    spawner.profile_list = [
        {
            'display_name': 'CPU server',
            'slug': 'cpu',
            'default': True,
        },
    ]

    # Dynamically update profile_list based on user
    if gpu_access:
        spawner.log.info(f"GPU access options added for {username}.")
        spawner.profile_list.extend(
            [
                {
                    'display_name': 'GPU server',
                    'slug': 'gpu',
                    'kubespawner_override': {
                        'image': 'training/datascience:my_tag',
                    },
                },
            ]
        )

    # Let KubeSpawner inspect profile_list and decide what to return, it
    # will return a falsy blank string if there is no profile_list,
    # which makes no options form be presented.
    #
    # ref: https://github.com/jupyterhub/kubespawner/blob/37a80abb0a6c826e5c118a068fa1cf2725738038/kubespawner/spawner.py#L1885-L1935
    return spawner._options_form_default()

# Don't forget to ask KubeSpawner to make use of this custom hook
c.KubeSpawner.options_form = custom_options_form