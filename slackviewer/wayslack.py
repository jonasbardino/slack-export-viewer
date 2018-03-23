#!/usr/bin/python
#
# Prepare wayslack dump direct messages for slack-export-viewer
#


"""Simple helper to create a suitable direct message setup with dms.json and
links to individual message dirs for the running of slack-export-viewer .
Uses the direct messages and index downloaded by wayslack into ims.json and
individual user dirs in _private/default/_ims .
"""

import click
import json
import logging
import os
import sys

_log_levels = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO,
               'WARNING': logging.WARNING, 'ERROR': logging.ERROR,
               'CRITICAL': logging.CRITICAL}
_ims_subdir = "_private/default/_ims"

def prepare_for_sev(wayslack_base, own_slack_id):
    """"""
    ims_base = os.path.normpath(os.path.join(wayslack_base, _ims_subdir))
    ims_json_path = os.path.join(ims_base, "ims.json")
    dms_json_path = os.path.join(wayslack_base, "dms.json")

    # Load ims and extend with members for each before writing to dms
    try:
        ims_fd = open(ims_json_path, "rb")
        ims_contents = json.load(ims_fd)
        ims_fd.close()
        logging.info("loaded %d ims entries from %s" % (len(ims_contents),
                                                        ims_json_path))
    except Exception, exc:
        logging.error("failed to load ims from %s : %s" % (ims_json_path, exc))
        return 1
    logging.debug("loaded ims contents: %s" % ims_contents)
    dms_contents = []
    skipped = []
    for entry in ims_contents:
        try:
            msg_base = os.path.join(ims_base, entry["id"])
            if not os.path.exists(msg_base):
                skipped.append(entry)
                logging.debug("skip handling of %(id)s with no message dir" % \
                              entry)
                continue
            link_path = os.path.join(wayslack_base, entry["id"])
            if not os.path.exists(link_path):
                logging.info("symlinked %s to %s" % (link_path, msg_base))
                os.symlink(msg_base, link_path)
        except Exception, exc:
            logging.warning("failed to link %s here : %s" % (msg_base, exc))
            continue
        entry["members"] = [own_slack_id, entry["user"]]
        logging.debug("added members to entry: %s" % entry)
        dms_contents.append(entry)

    logging.info("skipped %d user entries without chats" % len(skipped))
    logging.debug("saving generated dms %s" % dms_contents)
    try:
        dms_fd = open(dms_json_path, "wb")
        json.dump(dms_contents, dms_fd)
        dms_fd.close()
        logging.info("saved %d generated dms entries to %s" % \
                     (len(dms_contents), dms_json_path))
    except Exception, exc:
        logging.error("failed to save dms to %s : %s" % (dms_json_path, exc))
        return 1
    return 0

@cli.command(help="Prepares wayslack dump for slack-export-viewer run")
@click.option("-z", "--archive", type=click.Path(), required=True,
              default=envvar('SEV_ARCHIVE', ''),
              help="Path to your wayslack dump (directory)")
@click.option("-u", "--user_id", is_flag=True,
              default=flag_envvar('SEV_USER_ID', ''), required=True,
              help="Your own SLACK identity string from users.json")
@click.option("l", "--log_level", is_flag=True,
              default=flag_envvar('SEV_LOG_LEVEL', 'INFO'), 
              help="Amount of output using standard level names (%s)" % \
              ', '.join(_log_levels.keys()))
def main(archive, user_id, log_level):
    if not log_level.upper() in _log_levels:
        log_level = "INFO"
    logging.basicConfig(stream=sys.stdout, level=_log_levels[log_level],
                        format='%(asctime)s %(levelname)s %(message)s')
    retval = prepare_for_sev(archive, user_id)
    sys.exit(retval)
