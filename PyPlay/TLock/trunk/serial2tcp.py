#!/usr/bin/env python

# (C) 2002-2009 Chris Liechti <cliechti@gmx.net>
# redirect data from a TCP/IP connection to a serial port and vice versa
# requires Python 2.2 'cause socket.sendall is used


import sys
import os
import time
import threading
import multiprocessing
import socket
import codecs
import serial
try:
    True
except NameError:
    True = 1
    False = 0

def start_redirector( v, com_port, baudrate, tcp_port ):
    ser = serial.Serial()
    ser.port     = com_port
    ser.baudrate = baudrate
    ser.timeout  = 1     # required so that the reader thread can exit

    try:
        ser.open()
    except serial.SerialException, e:
        sys.stderr.write("Could not open serial port %s: %s\n" % (ser.portstr, e))
        sys.exit(1)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind( ('', tcp_port) )
    srv.listen(1)

    connection, addr = srv.accept()
    r = Redirector( v, ser, connection )
    r.shortcut()

class Redirector:
    def __init__(self, alive, serial_instance, socket, ser_newline=None, net_newline=None, spy=False):
        self.alive = alive
        self.serial = serial_instance
        self.socket = socket
        self.ser_newline = ser_newline
        self.net_newline = net_newline
        self.spy = spy
        self._write_lock = threading.Lock()

    @staticmethod
    def start_process( com_port, baudrate, tcp_port ):
        v = multiprocessing.Value( 'd', 1 )
        p = multiprocessing.Process( 
            target = start_redirector, 
            args = (v, com_port, baudrate, tcp_port) )

        p.start()
        return p, v
        
    @staticmethod
    def stop_process( data ):
        p, v = data
        v.value = 0
        p.join()

    def shortcut(self):
        """connect the serial port to the TCP port by copying everything
           from one side to the other"""
        #self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.setDaemon(True)
        self.thread_read.setName('serial->socket')
        self.thread_read.start()
        self.writer()

    def reader(self):
        """loop forever and copy serial->socket"""
        while self.alive.value:
            try:
                data = self.serial.read(1)              # read one, blocking
                n = self.serial.inWaiting()             # look if there is more
                if n:
                    data = data + self.serial.read(n)   # and get as much as possible
                if data:
                    # the spy shows what's on the serial port, so log it before converting newlines
                    if self.spy:
                        sys.stdout.write(codecs.escape_encode(data)[0])
                        sys.stdout.flush()
                    if self.ser_newline and self.net_newline:
                        # do the newline conversion
                        # XXX fails for CR+LF in input when it is cut in half at the begin or end of the string
                        data = net_newline.join(data.split(ser_newline))
                    # escape outgoing data when needed (Telnet IAC (0xff) character)
                    self._write_lock.acquire()
                    try:
                        self.socket.sendall(data)           # send it over TCP
                    finally:
                        self._write_lock.release()
            except socket.error, msg:
                sys.stderr.write('ERROR: %s\n' % msg)
                # probably got disconnected
                break
        #self.alive = False

    def write(self, data):
        """thread safe socket write with no data escaping. used to send telnet stuff"""
        self._write_lock.acquire()
        try:
            self.socket.sendall(data)
        finally:
            self._write_lock.release()

    def writer(self):
        """loop forever and copy socket->serial"""
        while self.alive.value:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                if self.ser_newline and self.net_newline:
                    # do the newline conversion
                    # XXX fails for CR+LF in input when it is cut in half at the begin or end of the string
                    data = ser_newline.join(data.split(net_newline))
                self.serial.write(data)                 # get a bunch of bytes and send them
                # the spy shows what's on the serial port, so log it after converting newlines
                if self.spy:
                    sys.stdout.write(codecs.escape_encode(data)[0])
                    sys.stdout.flush()
            except socket.error, msg:
                sys.stderr.write('ERROR: %s\n' % msg)
                # probably got disconnected
                break
        #self.alive = False
        self.thread_read.join()

    def stop(self):
        """Stop copying"""
        if self.alive:
            self.alive = False
            self.thread_read.join()
