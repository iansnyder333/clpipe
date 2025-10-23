import clpipe, nipype, traits, nibabel, nilearn, dcm2bids, heudiconv, bids, packaging
from clpipe.error_handler import exception_handler

print("OK clpipe:", clpipe.__file__)
print("nipype:", nipype.__version__, "traits:", traits.__version__)
print("nilearn:", nilearn.__version__, "nibabel:", nibabel.__version__)
print("dcm2bids:", dcm2bids.__version__, "heudiconv:", heudiconv.__version__)
print("pybids:", bids.__version__, "packaging:", packaging.__version__)
print("exception_handler import OK")

from clpipe.error_handler import exception_handler

print("exception_handler is callable:", callable(exception_handler))
