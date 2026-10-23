from minefleetsim_fleet.logic import TunnelLease
import pytest


def test_single_exclusive_owner():
    lease = TunnelLease()
    assert lease.request('robot_1') is True
    assert lease.request('robot_2') is False
    assert lease.owner == 'robot_1'
    lease.release('robot_1')
    assert lease.request('robot_2') is True
    assert lease.owner == 'robot_2'


def test_duplicate_wait_request_only_queued_once():
    lease = TunnelLease()
    lease.request('robot_1')
    for _ in range(5):
        assert lease.request('robot_2') is False
    assert lease.queue == ['robot_2']


def test_non_owner_cannot_release():
    lease = TunnelLease()
    lease.request('robot_1')
    with pytest.raises(ValueError):
        lease.release('robot_2')
