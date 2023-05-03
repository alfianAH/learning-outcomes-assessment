class ConditionTimeoutException(Exception):
    """
    Used when generating nilai and if it takes time longer than timeout.
    """
    pass


class DeleteLockedObjectException(Exception):
    """
    Used when locked object want to be deleted
    """
    pass


class SaveLockedObjectException(Exception):
    """
    Used when locked object want to be saved
    """
    pass
