
from tastypie.authorization import Authorization, ReadOnlyAuthorization  # DjangoAuthorization


"""
Authorizations
"""


class PerUserAuthorizationMixIn:
    def _per_user_check(self, object_list, bundle, is_list=False):
        if not hasattr(bundle.request, 'user'):
            return False
        user = bundle.request.user

        if is_list:
            if not user.is_superuser:
                object_list = object_list.filter(user_pk=user.pk)
            return object_list
        else:
            #if bundle.obj.pk:
            return bundle.obj.user_pk == user.pk
            #else:
            #    return True

    def read_list(self, object_list, bundle):
        return self._per_user_check(object_list, bundle, is_list=True)

    def read_detail(self, object_list, bundle):
        return self._per_user_check(object_list, bundle)


#class DisallowReadMixIn:
#    def read_list(self, object_list, bundle):
#        return False
#
#    def read_detail(self, object_list, bundle):
#        return False


class DisallowUpdateMixIn:
    def update_list(self, object_list, bundle):
        return []

    def update_detail(self, object_list, bundle):
        return False


class DisallowDeleteMixIn:
    def delete_list(self, object_list, bundle):
        return []

    def delete_detail(self, object_list, bundle):
        return False


class PerUserCreateReadAuthorization(PerUserAuthorizationMixIn, DisallowUpdateMixIn, DisallowDeleteMixIn, Authorization):
    pass


class PerUserReadOnlyAuthorization(PerUserAuthorizationMixIn, ReadOnlyAuthorization):
    pass
