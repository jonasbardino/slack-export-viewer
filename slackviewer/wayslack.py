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
import io
import json
import logging
import os
import sys

from slackviewer.utils.click import envvar

_log_levels = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO,
               'WARNING': logging.WARNING, 'ERROR': logging.ERROR,
               'CRITICAL': logging.CRITICAL}
_ims_subdir = "_private/default/_ims"
_groups_subdir = "_private/default/_groups"

def prepare_for_sev(wayslack_base, own_slack_id):
    """"""
    ims_base = os.path.normpath(os.path.join(wayslack_base, _ims_subdir))
    ims_json_path = os.path.join(ims_base, "ims.json")
    dms_json_path = os.path.join(wayslack_base, "dms.json")
    combined_base = os.path.normpath(os.path.join(wayslack_base, _groups_subdir))
    combined_json_path = os.path.join(combined_base, "groups.json")
    mpims_json_path = os.path.join(wayslack_base, "mpims.json")
    gdms_json_path = os.path.join(wayslack_base, "groups.json")
    svai_json_path = os.path.join(wayslack_base,
                                  ".slackviewer_archive_info.json")

    # Write a dummy svai file to mimic export unpacking, if not already there
    if not os.path.exists(svai_json_path):
        svai_contents = {"empty_dms": []}
        try:
            with io.open(svai_json_path, "w", encoding="utf8") as f:
                json.dump(svai_contents, f)
            logging.info("saved basic svai contents to %s" % svai_json_path)
        except Exception as exc:
            logging.error("failed to init svai to %s : %s" % (svai_json_path, exc))
            return 1

    # Shared dict for keeping track of empty entries
    skipped = {'ims': [], 'groups': []}

    # Load ims and extend with members for each before writing to dms
    try:
        with io.open(ims_json_path, "r", encoding="utf8") as f:
            ims_contents = json.load(f)
        logging.info("loaded %d ims entries from %s" % (len(ims_contents),
                                                        ims_json_path))
    except Exception as exc:
        logging.error("failed to load ims from %s : %s" % (ims_json_path, exc))
        return 1
    logging.debug("loaded ims contents: %s" % ims_contents)
    dms_contents = []
    for entry in ims_contents:
        try:
            msg_base = os.path.join(ims_base, entry["id"])
            if not os.path.exists(msg_base):
                skipped["ims"].append(entry)
                logging.debug("skip handling of %(id)s with no message dir" % \
                              entry)
                continue
            link_path = os.path.join(wayslack_base, entry["id"])
            if not os.path.exists(link_path):
                logging.info("symlinked %s to %s" % (link_path, msg_base))
                os.symlink(msg_base, link_path)
        except Exception as exc:
            logging.warning("failed to link %s here : %s" % (msg_base, exc))
            continue
        entry["members"] = [own_slack_id, entry["user"]]
        logging.debug("added members to entry: %s" % entry)
        dms_contents.append(entry)

    logging.info("skipped %d ims entries without chats" % len(skipped["ims"]))
    logging.debug("saving generated dms %s in %s" % (dms_contents,
                                                     dms_json_path))
    try:
        with io.open(dms_json_path, "w", encoding="utf8") as f:
            json.dump(dms_contents, f)
        logging.info("saved %d generated dms entries to %s" % \
                     (len(dms_contents), dms_json_path))
    except Exception as exc:
        logging.error("failed to save dms to %s : %s" % (dms_json_path, exc))
        return 1

    # Load combined groups and split out into gdms and mpims
    try:
        with io.open(combined_json_path, "r", encoding="utf8") as f:
            combined_contents = json.load(f)
        logging.info("loaded %d groups entries from %s" % (len(combined_contents),
                                                           combined_json_path))
    except Exception as exc:
        logging.error("failed to load groups from %s : %s" % (combined_json_path, exc))
        return 1
    logging.debug("loaded combined groups contents: %s" % combined_contents)
    mpims_contents, gdms_contents = [], []
    for entry in combined_contents:
        if not entry.get("id", None):
            logging.debug("skip handling of entry without id: %s" % entry)
            continue
        try:
            msg_base = os.path.join(combined_base, entry["id"])
            if not os.path.exists(msg_base):
                skipped["groups"].append(entry)
                logging.debug("skip handling of %(id)s with no message dir" % \
                              entry)
                continue
            # NOTE: symlink with name here
            link_path = os.path.join(wayslack_base, entry["name"])
            if not os.path.exists(link_path):
                logging.info("symlinked %s to %s" % (link_path, msg_base))
                os.symlink(msg_base, link_path)
        except Exception as exc:
            logging.warning("failed to link %s here : %s" % (msg_base, exc))
            continue
        if entry["is_mpim"]:
            mpims_contents.append(entry)
        elif entry["is_group"]:
            gdms_contents.append(entry)
        else:
            logging.warning("no handler for groups entry: %s" % entry)

    logging.info("skipped %d mpims/gdms entries without chats" % \
                 len(skipped["groups"]))

    logging.debug("saving generated mpims %s in %s" % (mpims_contents,
                                                       mpims_json_path))
    try:
        with io.open(mpims_json_path, "w", encoding="utf8") as f:
            json.dump(mpims_contents, f)
        logging.info("saved %d generated mpims entries to %s" % \
                     (len(mpims_contents), mpims_json_path))
    except Exception as exc:
        logging.error("failed to save mpims to %s : %s" % (mpims_json_path, exc))
        return 1
    logging.debug("saving generated gdms %s in %s" % (gdms_contents,
                                                      gdms_json_path))
    try:
        with io.open(gdms_json_path, "w", encoding="utf8") as f:
            json.dump(gdms_contents, f)
        logging.info("saved %d generated gdms entries to %s" % \
                     (len(gdms_contents), gdms_json_path))
    except Exception as exc:
        logging.error("failed to save gdms to %s : %s" % (gdms_json_path, exc))
        return 1

    logging.info("Now run slack-export-viewer with %s as target archive" % \
                 wayslack_base)
    return 0

@click.command(help="Prepares wayslack dump for slack-export-viewer run")
@click.option("-z", "--archive", type=click.Path(),
              default=envvar('SEV_ARCHIVE', '.'),
              help="Path to your wayslack dump (directory)")
@click.option("-u", "--user_id", required=True,
              help="Your own SLACK identity string from users.json")
@click.option("-l", "--log_level", default='INFO',
              help="Amount of output using standard level names (%s)" % \
              ', '.join(list(_log_levels.keys())))
def main(archive, user_id, log_level):
    log_level = log_level.upper()
    if not log_level in _log_levels:
        log_level = "INFO"
    logging.basicConfig(stream=sys.stdout, level=_log_levels[log_level],
                        format='%(asctime)s %(levelname)s %(message)s')
    retval = prepare_for_sev(archive, user_id)
    sys.exit(retval)
