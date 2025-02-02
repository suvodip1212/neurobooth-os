# -*- coding: utf-8 -*-
"""
"""

import os
import socket
import time
import psutil

import numpy as np

from neurobooth_os import config
from neurobooth_os.netcomm import (
    socket_message,
    socket_time,
    start_server,
    kill_pid_txt,
)


def _get_nodes(nodes):
    if isinstance(nodes, str):
        nodes = nodes
    return nodes


def start_servers(nodes=("acquisition", "presentation")):
    """Start servers

    Parameters
    ----------
    nodes : tuple, optional
        The nodes at which to start server, by default ("acquisition", "presentation")
    """
    kill_pid_txt()
    nodes = _get_nodes(nodes)
    for node in nodes:
        start_server(node)


def shut_all(nodes=("acquisition", "presentation")):
    """Shut all nodes

    Parameters
    ----------
    nodes : tuple | str
        The node names
    """
    nodes = _get_nodes(nodes)
    for node in nodes:
        socket_message("shutdown", node)
    time.sleep(10)
    # kill_pid_txt()  # TODO only if error


def test_lan_delay(n=100, nodes=("acquisition", "presentation")):
    """Test LAN delay

    Parameters
    ----------
    n : int
        The number of iterations
    nodes : tuple | str
        The node names
    """
    nodes = _get_nodes(nodes)
    times_1w, times_2w = [], []

    for node in nodes:
        tmp = []
        for i in range(n):
            tmp.append(socket_time(node, 0))
        times_1w.append([t[1] for t in tmp])
        times_2w.append([t[0] for t in tmp])

    _ = [
        print(
            f"{n} socket connexion time average:\n\t receive: {np.mean(times_2w[i])}\n\t send:\t  {np.mean(times_1w[i])} "
        )
        for i, n in enumerate(nodes)
    ]

    return times_2w, times_1w


def initiate_labRec():
    # Start LabRecorder
    if "LabRecorder.exe" not in (p.name() for p in psutil.process_iter()):
        os.startfile(config.neurobooth_config["LabRecorder"])

    time.sleep(0.05)
    s = socket.create_connection(("localhost", 22345))
    s.sendall(b"select all\n")
    s.close()
