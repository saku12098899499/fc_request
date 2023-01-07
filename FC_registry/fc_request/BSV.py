#!/usr/bin/env python3
# coding: utf-8
import subprocess
import sys
import json
import socket
import binascii

import time
import datetime
import numpy as np
import hashlib
 

ip_address = "127.0.0.1" # localhost
port_number = 18333
np.random.seed(12345) # for nonce of ping
path_bitcoin_cli = "/home/masaki/bitcoin-sv/src/" # path to bitcoin-cli <-- *** ここを変更する ***
wallet_address = "" # bsv testnet address <-- *** ここを変更する(事前にfaucetでbitcoinを入金しておくこと) ***
network_magic = "f4e5f3f4" # BSV, Testnet
tx_fee = 0.000007 # bsv
text_to_write = "" # texts to write  <-- *** ここを変更する ***


# functions for creating tx
def get_unspent(path_bitcoin_cli, wallet_address):
  cmd = path_bitcoin_cli+"bitcoin-cli listunspent"
  #print(cmd)
  try:
    response = (subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE).communicate()[0]).decode("utf-8")
  except:
    print("Error of running bitcoin-cli, exit...")
    sys.exit(1)
  data_list = json.loads(response)
  #print(data_dict)
  for item in data_list:
    if item["address"] == wallet_address and item["amount"] > tx_fee and item["spendable"] == True:
      print("yes")
      #print(item)
      return item 



def generate_raw_tx(unspent_data):
  nVersion = "02000000"
  inCnt = "01"
  prevTXID_orig = unspent_data["txid"]
  prevTXID = be2le(prevTXID_orig)
  prevVout_orig = str(unspent_data["vout"])
  prevVout = be2le("0"*(8-len(prevVout_orig))+prevVout_orig)
  #prevScriptPubKey = unspent_data["scriptPubKey"]
  prevScriptPubKey = ""
  prevScriptPubKeySize = str(f'{int(len(prevScriptPubKey)/2):02x}')
  print(prevScriptPubKeySize)
  sequence = "ffffffff"
  scriptPubKey = unspent_data["scriptPubKey"]
  scriptPubKeySize = str(hex(int(len(scriptPubKey)/2))).replace("0x", "")
  outCnt = "01"
  prevAmount = unspent_data["amount"]
  amount = be2le( format(int((prevAmount - tx_fee)*(10**8)), "016x") )
  locktime = "00000000"

  #print(nVersion, inCnt, prevTXID_orig, prevTXID, prevVout_orig, prevVout, prevScriptPubKey, prevScriptPubKeySize, sequence, scriptPubKey, scriptPubKeySize, outCnt, prevAmount, amount, locktime)
  raw_tx = nVersion+inCnt+prevTXID+prevVout+prevScriptPubKeySize+prevScriptPubKey+sequence+outCnt+amount+scriptPubKeySize+scriptPubKey+locktime
  return raw_tx


# http://gurapomu.hatenablog.com/entry/2018/02/19/162753
def generate_op_return_tx(unspent_data, text_to_write):
  nVersion = "02000000"
  inCnt = "01"
  prevTXID_orig = unspent_data["txid"]
  prevTXID = be2le(prevTXID_orig)
  prevVout_orig = str(unspent_data["vout"])
  prevVout = be2le("0"*(8-len(prevVout_orig))+prevVout_orig)
  #prevScriptPubKey = unspent_data["scriptPubKey"]
  prevScriptPubKey = ""
  prevScriptPubKeySize = str(f'{int(len(prevScriptPubKey)/2):02x}')
  #print(prevScriptPubKeySize)
  sequence = "ffffffff"

  scriptPubKey = unspent_data["scriptPubKey"]
  scriptPubKeySize = str(hex(int(len(scriptPubKey)/2))).replace("0x", "")

  outCnt = "02"
  prevAmount = unspent_data["amount"]

  amount = be2le( format(int((prevAmount - tx_fee)*(10**8)), "016x") )
  amount2 = "0"*16 # 0 bsv for op_return

  print("The length of text to write:", len(text_to_write))
  if len(text_to_write) < 76:
    bin_text_to_write = binascii.hexlify(text_to_write.encode())
    bin_text_to_write_length = str(hex(int(len(bin_text_to_write.decode())/2))).replace("0x", "")
    if len(bin_text_to_write_length) == 1:
      bin_text_to_write_length = "0"+bin_text_to_write_length
    # op_false : 0x00
    # op_return: 0x6a
    scriptPubKey2 = "006a"+bin_text_to_write_length+bin_text_to_write.decode()
    print(scriptPubKey2)
    scriptPubKeySize2 = str(hex(int(len(scriptPubKey2)/2))).replace("0x", "")
    if len(scriptPubKeySize2) == 1:
      scriptPubKeySize2 = "0"+scriptPubKeySize2
    print(scriptPubKeySize2)
    #sys.exit(0)
  elif len(text_to_write) < 256:
    bin_text_to_write = binascii.hexlify(text_to_write.encode())
    bin_text_to_write_length = str(hex(int(len(bin_text_to_write.decode())/2))).replace("0x", "")
    # op_false : 0x00
    # op_return: 0x6a
    scriptPubKey2 = "006a4c"+bin_text_to_write_length+bin_text_to_write.decode()
    scriptPubKeySize2 = str(hex(int(len(scriptPubKey2)/2))).replace("0x", "")
  elif len(text_to_write) < 65536:
    bin_text_to_write = binascii.hexlify(text_to_write.encode())
    print(bin_text_to_write, len(bin_text_to_write))
    bin_text_to_write_length = str(hex(int(len(bin_text_to_write.decode())/2))).replace("0x", "")
    bin_text_to_write_length = "0"*(4-len(bin_text_to_write_length))+bin_text_to_write_length
    bin_text_to_write_length = be2le(bin_text_to_write_length)
    print(bin_text_to_write_length)
    # op_false : 0x00
    # op_return: 0x6a
    scriptPubKey2 = "006a4d"+bin_text_to_write_length+bin_text_to_write.decode()
    scriptPubKeySize2 = str(hex(int(len(scriptPubKey2)/2))).replace("0x", "")
    scriptPubKeySize2 = "0"*(4-len(scriptPubKeySize2))+scriptPubKeySize2
    # VARINT: Prefix with "fd"
    # https://learnmeabitcoin.com/technical/varint
    scriptPubKeySize2 = "fd"+be2le(scriptPubKeySize2)
    print(scriptPubKeySize2)
  else:
    print("more than 65535 letters, exit.")
    sys.exit(1)

  locktime = "00000000"

  #print(nVersion, inCnt, prevTXID_orig, prevTXID, prevVout_orig, prevVout, prevScriptPubKey, prevScriptPubKeySize, sequence, scriptPubKey, scriptPubKeySize, outCnt, prevAmount, amount, locktime)
  raw_tx = nVersion+inCnt+prevTXID+prevVout+prevScriptPubKeySize+prevScriptPubKey+sequence+outCnt+amount+scriptPubKeySize+scriptPubKey+amount2+scriptPubKeySize2+scriptPubKey2+locktime
  return raw_tx





def generate_signed_tx(raw_tx):
  cmd = path_bitcoin_cli+"bitcoin-cli signrawtransaction "+raw_tx
  cmd=(subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE).communicate()[0])
  print(cmd)
  try:
    response = bytes.fromhex(cmd).decode("utf-8")
  except:
    print("Error of running bitcoin-cli, exit...")
    sys.exit(1)
  data_dict = json.loads(response)
    
  signed_tx = data_dict["hex"]
  return signed_tx


def decode_raw_transaction(signed_tx):
  cmd = path_bitcoin_cli+"bitcoin-cli decoderawtransaction "+signed_tx
  #print(cmd)
  try:
    response = (subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE).communicate()[0]).decode("utf-8")
  except:
    print("Error of running bitcoin-cli, exit...")
    sys.exit(1)
  data_dict = json.loads(response)
  print(data_dict)



# functions for sending tx
def get_latest_block_count(path_bitcoin_cli):
  cmd = path_bitcoin_cli+"bitcoin-cli getinfo"
  #print(cmd)
  try:
    response = (subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE).communicate()[0]).decode("utf-8")
  except:
    print("Error of running bitcoin-cli, exit...")
    sys.exit(1)
  data_dict = json.loads(response)
  return "0"*(8-len(str(data_dict["blocks"])))+str(data_dict["blocks"]) # the latest block # (8 digits)


def receive_all(sock, buffer_size=4096):
  data_str = ""
  while True:
    time.sleep(0.5)
    data = sock.recv(buffer_size)
    data_str += bytes.hex(data)
    print("receive_all:", data_str, len(data_str))
    if len(data) < buffer_size:
      break
  return data_str


def be2le(hex_be): # big endian --> little endian conversion
  bytes_be = binascii.unhexlify(hex_be)
  bytes_le = bytes_be[::-1]
  hex_le = binascii.hexlify(bytes_le).decode()
  return hex_le


def generate_msg_version():
  ### create payload ###
  version = "7f110100"
  services1 = "2500000000000000"
  services2 = "2504000000000000"
  timestamp_be = format(int(datetime.datetime.now().timestamp()), '016x')
  timestamp_le = be2le(timestamp_be)
  network_port_be = format(18333, '04x')
  ip_address_hex = format(127, '02x')+format(0, '02x')+format(0, '02x')+format(1, '02x')
  addr_recv = services1+"0"*20+"ffff"+ip_address_hex+network_port_be
  addr_from = services2+"0"*36
  nonce = format(np.random.randint(0, 2**32), "04x")+format(np.random.randint(0, 2**32), "04x")
  user_agent = str(binascii.hexlify(b"/Bitcoin SV:1.0.2/"), "utf-8")
  user_agent_size = format(int(len(user_agent)/2), "02x")

  latest_block_count = get_latest_block_count(path_bitcoin_cli)
  #print("The latest block #:", latest_block_count)

  block_height = be2le(latest_block_count)
  relay = "01"
  payload  = version+services1+timestamp_le+addr_recv+addr_from+nonce+user_agent_size+user_agent+block_height+relay
  #print("payload:", payload)
  
  ### create version binary ###
  command_tmp = str(binascii.hexlify(b"version"), "utf-8")
  command = command_tmp + "0"*(24-len(command_tmp))

  payload_length_be = format(int(len(payload)/2), "08x")
  payload_length_le = be2le(payload_length_be)

  payload_hash_tmp = hashlib.sha256(bytes.fromhex(payload)).hexdigest()
  payload_hash = hashlib.sha256(bytes.fromhex(payload_hash_tmp)).hexdigest()

  payload_checksum = payload_hash[0:8]

  header = network_magic+command+payload_length_le+payload_checksum
  #print("header:", header)
  
  msg_version = header+payload
  #print(msg_version)
  return msg_version

def generate_msg_verack():
  payload = "" # payload is empty

  command_tmp = str(binascii.hexlify(b"verack"), "utf-8")
  command = command_tmp + "0"*(24-len(command_tmp))
  #print(command)

  payload_length_le = "0"*8

  payload_checksum = "5df6e0e2"

  header = network_magic+command+payload_length_le+payload_checksum
  verack_message = header+payload

  return verack_message


def generate_inv(doublehash_signed_tx):
  number_of_objects = "01" # 1
  type_identifier = "01000000" # MSG_TX
  payload = number_of_objects+type_identifier+doublehash_signed_tx

  command_tmp = str(binascii.hexlify(b"inv"), "utf-8")
  command = command_tmp + "0"*(24-len(command_tmp))

  payload_length_be = format(int(len(payload)/2), "08x")
  payload_length_le = be2le(payload_length_be)

  payload_hash_tmp = hashlib.sha256(bytes.fromhex(payload)).hexdigest()
  payload_hash = hashlib.sha256(bytes.fromhex(payload_hash_tmp)).hexdigest()
  payload_checksum = payload_hash[0:8]

  header = network_magic+command+payload_length_le+payload_checksum

  inv_message = header+payload

  return inv_message


def generate_tx(signed_tx):
  payload = signed_tx

  command_tmp = str(binascii.hexlify(b"tx"), "utf-8")
  command = command_tmp + "0"*(24-len(command_tmp))

  payload_length_be = format(int(len(payload)/2), "08x")
  payload_length_le = be2le(payload_length_be)

  payload_hash_tmp = hashlib.sha256(bytes.fromhex(payload)).hexdigest()
  payload_hash = hashlib.sha256(bytes.fromhex(payload_hash_tmp)).hexdigest()
  payload_checksum = payload_hash[0:8]

  header = network_magic+command+payload_length_le+payload_checksum

  inv_message = header+payload

  return inv_message





""" トランザクションの送信 """
def post(textdata,walletdata):
  # get unspent data
  text_to_write = textdata
  wallet_address = walletdata
  print("^^^^^^^^^^^^^^^^^^^^^^")
  print(textdata)
  #print(wallet)
  print("^^^^^^^^^^^^^^^^^^^^^^")
  unspent_data = get_unspent(path_bitcoin_cli, wallet_address)
  #print(unspent_data)

  # create tx
  #raw_tx = generate_raw_tx(unspent_data)
  print("text to write:", text_to_write)
  raw_tx = generate_op_return_tx(unspent_data, text_to_write)
  #print("raw tx:", raw_tx, len(raw_tx))
  #sys.exit(0)

  # create signed tx
  signed_tx = generate_signed_tx(raw_tx)
  #print("signed tx:", signed_tx)

  # decode signed tx
  decode_raw_transaction(signed_tx)

#  sys.exit(0)

  # create socket connection
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  print("### socket open ###")
  #print("### creating socket connection ... ###")
  s.connect((ip_address, port_number))
  print("### socket connected ###")

  print("### sending VERSION ... ###")
  msg_version = generate_msg_version()
  #print("VERSION:", msg_version)
  s.send(bytes.fromhex(msg_version))
  print("### VERSION sent ###")

  print("### waiting for VERSION and VERACK ... ###")
  while True:
    received_data_str = receive_all(s)
    msg_list = received_data_str.split(network_magic)
    print(msg_list)
    msg_version_received_flag = False
    msg_verack_received_flag = False
    msg_verack_sent = False

    for i, msg in enumerate(msg_list):
      if i == 0:
        continue # skip

      protocol_name = binascii.unhexlify(msg[0:24].rstrip('0')).decode('utf-8')
      print("-----")
      print("protocol name:", protocol_name, "; payload:", msg[40:])
      if protocol_name == "version":
        msg_version_received_flag = True
      elif protocol_name == "verack":
        msg_verack_received_flag = True
      else:
        None

      if msg_version_received_flag == True and msg_verack_received_flag == True: 
        print("### VERSION and VERACK received ###")
        print("### sending back VERACK ###")
        msg_verack = generate_msg_verack()
        s.send(bytes.fromhex(msg_verack))
        msg_verack_sent = True
        print("### VERACK sent ###")

    if msg_verack_sent == True:
      break


  # send INV message
  print("### senging INV message ... ###")
  h_tmp = hashlib.sha256(bytes.fromhex(signed_tx)).hexdigest()
  doublehash_signed_tx = hashlib.sha256(bytes.fromhex(h_tmp)).hexdigest()
  inv_message = generate_inv(doublehash_signed_tx)
  print("inv message:", inv_message)
  s.send(bytes.fromhex(inv_message))
  print("### INV sent ###")

  # receive GETDATA message
  while True:
    getdata_flag = False
    data_str = receive_all(s)
    msgList = data_str.split(network_magic)

    for i, msg in enumerate(msgList):
      if i == 0:
        continue

      command = binascii.unhexlify(msg[0:24].rstrip('0')).decode('utf-8')
      #print("command name:", command, "; payload:", msg[40:])

      if command == "getdata":
        getdata_flag = True

    if getdata_flag == True:
      break

  # send TX message
  #print("### senging TX ... ###")
  tx_message = generate_tx(signed_tx)
  #print(tx_message)
  s.send(bytes.fromhex(tx_message))
  print("### TX sent###")

  time.sleep(3) # wait 3 sec.

  s.close()
  print("### socket closed ###")

