# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from json import loads
from time import sleep

from moi import r_client

from qiita_db.processing_job import ProcessingJob


def wait_for_prep_information_job(prep_id, raise_if_none=True):
    """Waits until a prep information job is completed

    Parameters
    ----------
    prep_id : int
        Prep template id
    raise_if_none : bool, optional
        If True, raise an AssertionError if the correspondent redis key
        is empty. Default: True

    Raises
    ------
    AssertionError
        If `raise_if_none` is True and the correspondent redis key is not set
    """
    res = r_client.get('prep_template_%d' % prep_id)

    if raise_if_none and res is None:
        raise AssertionError("unexpectedly None")

    if res is not None:
        payload = loads(res)
        job_id = payload['job_id']
        if payload['is_qiita_job']:
            job = ProcessingJob(job_id)
            while job.status not in ('success', 'error'):
                sleep(0.05)
        else:
            redis_info = loads(r_client.get(job_id))
            while redis_info['status_msg'] == 'Running':
                sleep(0.05)
                redis_info = loads(r_client.get(job_id))
        sleep(0.05)
