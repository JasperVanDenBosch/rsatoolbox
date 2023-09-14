"""Just-in-time importing of optional dependencies 
"""


def import_nibabel():
    try:
        import nibabel
    except ImportError:
        raise OptionalImportMissingException('nibabel')
    return nibabel


class OptionalImportMissingException(Exception):

    def __init__(self, name: str):
        super().__init__(f'Missing optional dependency: {name}')
