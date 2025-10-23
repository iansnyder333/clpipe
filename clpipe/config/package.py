PACKAGE_NAME = "clpipe"
# Bump for Py3.11 compatibility (packaging-only change)
VERSION = "1.9.2"

DESCRIPTION = "clpipe: MRI processing pipeline for high performance clusters"
REPO_URL = "https://github.com/cohenlabUNC/clpipe"
AUTHORS = (
    "Author/Maintainer: Teague Henry, Maintainer: Will Asciutto, "
    "Contributor: Bhvaith Manapoty, Contributor: Yuvraj Jain, Contributor: Deepak Melwani"
)
AUTHOR_EMAIL = "ycp6wm@virginia.edu"
LICENSE = "MIT"

# Minimum supported Python (broaden to cover Py3.11)
PYTHON_VERSION = "3.10"
PYTHON_REQUIRES = f">={PYTHON_VERSION}"

# List of all dependency packages, to be automatically installed alongside clpipe
INSTALL_REQUIRES = [
    # keep exact pins where they’re harmless; widen where Py3.11 needs it
    "jsonschema>=4.17,<5",
    "click>=8.1.3,<9",
    # Py3.11-safe scientific stack
    "numpy>=1.26,<2",  # conservative upper; NumPy 2.x is WIP across ecosystem
    "scipy>=1.11,<1.12",
    "pandas>=2.2,<2.3",
    "nibabel>=5.2",  # Py3.11 support line
    "nilearn>=0.10,<0.13",  # 0.10 supports modern Python; keep an upper cushion
    # orchestration & BIDS/fMRIPrep deps
    "dcm2bids==2.1.9",
    "nipype>=1.8.6",  # works on 3.11 when traits < 6.4
    "traits<6.4",
    "pybids>=0.15.6",
    "templateflow==23.0.0",
    # utilities
    "packaging>=23",  # replace any distutils/pkg_resources version parsing
    "pydantic==1.10.7",
    "matplotlib>=3.8",  # 3.8.x supports Python 3.11
    "heudiconv==0.12.2",
    "tqdm==4.65.0",
    "marshmallow-dataclass==8.5.14",
    "PyYAML>=6.0",
]


PACKAGE_DATA = {"clpipe": ["R_scripts/*.R"]}

# These entries register bash aliases to click commands. The aliases are available for
#   use upon package installation, and are implemented by auto-generated scripts in
#   <python env>/bin
ENTRY_POINTS = """
      [console_scripts]
      clpipe=clpipe.cli:cli
      project_setup=clpipe.cli:project_setup_cli
      convert2bids=clpipe.cli:convert2bids_cli
      bids_validate=clpipe.cli:bids_validate_cli
      fmriprep_process=clpipe.cli:fmriprep_process_cli
      fmri_postprocess=clpipe.cli:fmri_postprocess_cli
      fmri_postprocess2=clpipe.cli:fmri_postprocess2_cli
      postprocess_image=clpipe.cli:postprocess_image_cli
      glm_l1_preparefsf=clpipe.cli:glm_l1_preparefsf_cli
      glm_l1_launch=clpipe.cli:glm_l1_launch_cli
      glm_l2_preparefsf=clpipe.cli:glm_l2_preparefsf_cli
      glm_l2_launch=clpipe.cli:glm_l2_launch_cli
      fsl_onset_extract=clpipe.cli:fsl_onset_extract_cli
      fmri_process_check=clpipe.cli:fmriprep_process_cli
      get_reports=clpipe.cli:get_fmriprep_reports_cli
      get_config_file=clpipe.cli:get_config_cli
      get_glm_config_file=clpipe.cli:get_glm_config_cli
      fmri_roi_extraction=clpipe.cli:fmri_roi_extraction_cli
      test_batch_setup=clpipe.test_batch_setup:test_batch_setup
      get_available_atlases=clpipe.cli:get_available_atlases_cli
      update_config_file=clpipe.cli:update_config_cli
      templateflow_setup=clpipe.cli:templateflow_setup_cli
      test_func=clpipe.utils:test_func
      fmap_cleanup=clpipe.fmap_cleanup:fmap_cleanup
      reho_extract=clpipe.reho_extract:reho_extract
      t2star_extract=clpipe.t2star_extract:t2star_extract
"""
