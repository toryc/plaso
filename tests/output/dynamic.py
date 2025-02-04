#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the dynamic output module."""

from __future__ import unicode_literals

import unittest

from plaso.containers import events
from plaso.formatters import interface as formatters_interface
from plaso.formatters import manager as formatters_manager
from plaso.lib import definitions
from plaso.lib import timelib
from plaso.output import dynamic

from tests.cli import test_lib as cli_test_lib
from tests.output import test_lib


class TestEvent(events.EventObject):
  """Test event object."""
  DATA_TYPE = 'test:dynamic'

  def __init__(self):
    """Initializes an event object."""
    super(TestEvent, self).__init__()
    self.timestamp = timelib.Timestamp.CopyFromString('2012-06-27 18:17:01')
    self.timestamp_desc = definitions.TIME_DESCRIPTION_CHANGE
    self.hostname = 'ubuntu'
    self.filename = 'log/syslog.1'
    self.text = (
        'Reporter <CRON> PID: 8442 (pam_unix(cron:session): session\n '
        'closed for user root)')


class TestEventFormatter(formatters_interface.EventFormatter):
  """Test event formatter."""
  DATA_TYPE = 'test:dynamic'
  FORMAT_STRING = '{text}'

  SOURCE_SHORT = 'LOG'
  SOURCE_LONG = 'Syslog'


class DynamicOutputModuleTest(test_lib.OutputModuleTestCase):
  """Test the dynamic output module."""

  # TODO: add coverage for _FormatTag.

  def testHeader(self):
    """Tests the WriteHeader function."""
    output_mediator = self._CreateOutputMediator()
    output_writer = cli_test_lib.TestOutputWriter()
    output_module = dynamic.DynamicOutputModule(output_mediator)
    output_module.SetOutputWriter(output_writer)
    expected_header = (
        'datetime,timestamp_desc,source,source_long,message,parser,'
        'display_name,tag\n')

    output_module.WriteHeader()
    header = output_writer.ReadOutput()
    self.assertEqual(header, expected_header)

    output_mediator = self._CreateOutputMediator()
    output_writer = cli_test_lib.TestOutputWriter()
    output_module = dynamic.DynamicOutputModule(output_mediator)
    output_module.SetFields([
        'date', 'time', 'message', 'hostname', 'filename', 'some_stuff'])
    output_module.SetOutputWriter(output_writer)

    expected_header = 'date,time,message,hostname,filename,some_stuff\n'
    output_module.WriteHeader()
    header = output_writer.ReadOutput()
    self.assertEqual(header, expected_header)

    output_mediator = self._CreateOutputMediator()
    output_writer = cli_test_lib.TestOutputWriter()
    output_module = dynamic.DynamicOutputModule(output_mediator)
    output_module.SetFields([
        'date', 'time', 'message', 'hostname', 'filename', 'some_stuff'])
    output_module.SetFieldDelimiter('@')
    output_module.SetOutputWriter(output_writer)

    expected_header = 'date@time@message@hostname@filename@some_stuff\n'
    output_module.WriteHeader()
    header = output_writer.ReadOutput()
    self.assertEqual(header, expected_header)

  def testWriteEventBody(self):
    """Tests the WriteEventBody function."""
    formatters_manager.FormattersManager.RegisterFormatter(
        TestEventFormatter)

    event_object = TestEvent()

    output_mediator = self._CreateOutputMediator()
    output_writer = cli_test_lib.TestOutputWriter()
    output_module = dynamic.DynamicOutputModule(output_mediator)
    output_module.SetFields([
        'date', 'time', 'timezone', 'macb', 'source', 'sourcetype',
        'type', 'user', 'host', 'message_short', 'message',
        'filename', 'inode', 'notes', 'format', 'extra'])
    output_module.SetOutputWriter(output_writer)

    output_module.WriteHeader()
    expected_header = (
        'date,time,timezone,macb,source,sourcetype,type,user,host,'
        'message_short,message,filename,inode,notes,format,extra\n')
    header = output_writer.ReadOutput()
    self.assertEqual(header, expected_header)

    output_module.WriteEventBody(event_object)
    expected_event_body = (
        '2012-06-27,18:17:01,UTC,..C.,LOG,Syslog,Metadata Modification Time,-,'
        'ubuntu,Reporter <CRON> PID: 8442 (pam_unix(cron:session): session '
        'closed for user root),Reporter <CRON> PID: 8442 '
        '(pam_unix(cron:session): session closed for user root),log/syslog.1'
        ',-,-,-,-\n')
    event_body = output_writer.ReadOutput()
    self.assertEqual(event_body, expected_event_body)

    output_mediator = self._CreateOutputMediator()
    output_writer = cli_test_lib.TestOutputWriter()
    output_module = dynamic.DynamicOutputModule(output_mediator)
    output_module.SetFields([
        'datetime', 'nonsense', 'hostname', 'message'])
    output_module.SetOutputWriter(output_writer)

    expected_header = 'datetime,nonsense,hostname,message\n'
    output_module.WriteHeader()
    header = output_writer.ReadOutput()
    self.assertEqual(header, expected_header)

    expected_event_body = (
        '2012-06-27T18:17:01+00:00,-,ubuntu,Reporter <CRON> PID: 8442'
        ' (pam_unix(cron:session): session closed for user root)\n')

    output_module.WriteEventBody(event_object)
    event_body = output_writer.ReadOutput()
    self.assertEqual(event_body, expected_event_body)

    formatters_manager.FormattersManager.DeregisterFormatter(
        TestEventFormatter)


if __name__ == '__main__':
  unittest.main()
