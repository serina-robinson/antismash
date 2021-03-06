# License: GNU Affero General Public License v3 or later
# A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.

""" A collection of functions for running hmmpfam2.
"""

from io import StringIO
import logging
from typing import List

from .base import execute, get_config, SearchIO


def run_hmmpfam2(query_hmmfile: str, target_sequence: str, extra_args: List[str] = None
                 ) -> List[SearchIO._model.query.QueryResult]:  # pylint: disable=protected-access
    """ Run hmmpfam2 over the provided HMM file and fasta input

        Arguments:
            query_hmmfile: the HMM file to use
            target_sequence: a string in fasta format of the sequence to run

        Returns:
            a list of results as parsed by SearchIO
    """
    config = get_config()
    command = [config.executables.hmmpfam2]

    # Only use multithreading in hmmpfam2 if supported in the hmmpfam2 build
    if " --cpu " in run_hmmpfam2_help():
        command.extend(["--cpu", str(config.cpus)])
    if extra_args:
        command.extend(extra_args)
    command.extend([query_hmmfile, '-'])

    result = execute(command, stdin=target_sequence)
    if not result.successful():
        logging.debug('hmmpfam2 returned %d: %r while searching %r', result.return_code,
                      result.stderr, query_hmmfile)
        raise RuntimeError("hmmpfam2 problem while running %s: %s" % (command, result.stderr))
    res_stream = StringIO(result.stdout)
    return list(SearchIO.parse(res_stream, 'hmmer2-text'))


def run_hmmpfam2_help() -> str:
    """ Get the help output of hmmpfam2 """

    # cache results
    help_text = getattr(run_hmmpfam2_help, 'help_text', '')
    if help_text:
        return help_text

    hmmpfam2 = get_config().executables.hmmpfam2
    command = [
        hmmpfam2,
        "-h",
    ]

    help_text = execute(command).stdout
    if not help_text.startswith("hmmpfam"):
        msg = "unexpected output from hmmpfam2: %s, check path"
        raise RuntimeError(msg % hmmpfam2)

    setattr(run_hmmpfam2_help, 'help_text', help_text)
    return help_text


def run_hmmpfam2_version() -> str:
    """ Get the version of the hmmpfam2 binary """
    version_line = run_hmmpfam2_help().split('\n')[1]
    return version_line.split()[1]
