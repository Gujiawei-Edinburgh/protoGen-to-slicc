import time
import sys
import json

from Parser.ClassProtoParser import ProtoParser
from Parser.ProtoCCLexer import ProtoCCLexer
from Parser.ProtoCCParser import ProtoCCParser
from Parser.ProtoCCcomTreeFct import *
from Algorithm.ProtoAlgorithm import ProtoAlgorithm
from Algorithm.ProtoConfig import ProtoConfig
from SLICCParser.ProtoGenParser import ProtoGenParser
from Murphi.Murphi import Murphi
from SLICCParser.ParseMurphy import ParseMurphy
from Monitor.Debug import *
import antlr3

file = "MSI_Proto.pcc"
cache_dest = open("MSI-cache.sm", 'w', encoding='utf-8')
dire_dest = open("MSI-dir.sm", 'w', encoding='utf-8')
msg_dest = open("MSI-message.sm", 'w', encoding='utf-8')

Parser = ProtoParser(file)
Config = ProtoConfig()
Algorithm = ProtoGenParser(Parser, Config)
cache_state_transitions = Algorithm.getCacheTransitions()
dir_state_transitions = Algorithm.getDirTransitions()
murphy_parser = ParseMurphy(file)
murphy_parser.getStableStates(cache_state_transitions)
murphy_parser.getMessageType(cache_state_transitions)
cache_transition_mapping = murphy_parser.getMappingTransition(cache_state_transitions)
dir_transitions_mapping = murphy_parser.getMappingTransition(dir_state_transitions)
# murphy_parser.writeActionsBlocks(destination, cache_state_transitions)
content_fwd = None
content_fwd = "in_port(fwdfrom_in, CoherenceMessage, fwdFrom) {\n"
content_fwd = content_fwd + '\t' + 'if (fwdfrom_in.isReady(clockEdge())) {\n'
content_fwd = content_fwd + '\t\t' + 'peek (fwdfrom_in, CoherenceMessage) {\n'
content_fwd = content_fwd + '\t\t\t' + 'TBE tbe := TBEs[in_msg.LineAddress];\n'
content_fwd = content_fwd + '\t\t\t' + 'Entry entry := getCacheEntry(in_msg.LineAddress);\n'
content_fwd = content_fwd + '\t\t\t' + 'State st := getState(tbe, entry, in_msg.LineAddress);\n'
content_fwd = content_fwd + '\t\t\t' + 'Addr LineAddress := in_msg.LineAddress;\n'
index_state = 0
for k in cache_transition_mapping:
    listTemp = cache_transition_mapping[k]
    if index_state == 0:
        content_fwd = content_fwd + '\t\t\t' + 'if (st == State:' + k + ') {\n'
        index_state = 1
    else:
        content_fwd = content_fwd + '\t\t\t' + 'else if (st == State:' + k + ') {\n'
    
    index_msg = 0
    is_else_statement = False
    is_if_statement = False
    #each start state and in_msg corresponding to switch state switch in_msg
    for each_entry in listTemp:
        in_msg = each_entry['in_msg']
        if in_msg == '' or in_msg is None:
            continue
        transition = each_entry['transition']
        if index_msg == 0:
            content_fwd = content_fwd + '\t\t\t\t' + 'if (in_msg.Type == CoherenceMessageType:' + in_msg + ') {\n' 
            index_msg = 1 
            is_if_statement = True
        else:
            content_fwd = content_fwd + '\t\t\t\t' + 'else if (in_msg.Type == CoherenceMessageType:' + in_msg + ') {\n'
            is_else_statement = True

        result_type, related_message = murphy_parser.getCacheFuncTargetCode(k, transition, in_msg)

        if result_type == -1:
            print(k + ':' + in_msg)
            print('------------------------------------------')
            print('cannot find the target code in Murphy file')
            print('------------------------------------------')
            # exit()

        if len(transition) == 1:
            for each in related_message:
                content_fwd += '\t' * 5 + related_message[each] + '\n'
            content_fwd = content_fwd + murphy_parser.getStateTransitionPart(in_msg, transition[0]['final_state'], transition[0])
        elif len(transition) == 2:
            content_fwd = content_fwd + '\t\t\t\t\t' + related_message['reg'] +'\n'
            content_fwd = content_fwd + '\t\t\t\t\t' + 'if (entry.acksExpectedL1 == entry.acksReceivedL1)  {\n'
            content_fwd = content_fwd + '\t\t\t\t\t\t' + 'entry.acksReceivedL1 := 0;\n' + '\t\t\t\t\t' + 'entry.acksExpectedL1 := 0;\n'
            content_fwd = content_fwd + murphy_parser.getStateTransitionPart(in_msg, transition[1]['final_state'], transition[1])
            content_fwd = content_fwd + '\t\t\t\t\t' + '}\n'
            content_fwd = content_fwd + '\t\t\t\t\t' +'else if(entry.acksExpectedL1 != entry.acksReceivedL1)  {\n'
            content_fwd = content_fwd + murphy_parser.getStateTransitionPart(in_msg, transition[0]['final_state'], transition[0])
            content_fwd += '\t' * 5 + '}\n'
        
        content_fwd = content_fwd + '\t\t\t\t' + '}\n'
    
    if is_else_statement or is_if_statement:
        content_fwd = content_fwd + '\t\t\t\t' + 'else {\n' + '\t\t\t\t\t' + '//stall\n'
        content_fwd = content_fwd + '\t\t\t\t' + '}\n'
    content_fwd = content_fwd + '\t\t\t' +'}\n'
    is_else_statement = False
    is_if_statement = False

content_fwd += '\t' * 3 + 'else {\n' + '\t' * 4 + 'error("Unrecognized state in in_port=respfrom_in!");\n' + '\t' * 3 + '}\n'
content_fwd = content_fwd + '\t\t' +'}\n'
content_fwd = content_fwd + '\t' +'}\n'
content_fwd = content_fwd +'}\n'
content_fwd = content_fwd.replace('__', '_')
content_req = content_fwd.replace('fwdfrom_in', 'reqfrom_in')
content_resp = content_fwd.replace('fwdfrom_in', 'respfrom_in')


file = open('SLICCParser/template.json')
json_str = file.read()
file.close()
template_json = json.loads(json_str)

final_cache = template_json['cache_header']        
content_in_port = content_fwd + '\n\n' + content_req + '\n\n' + content_resp + '\n\n' 
final_cache += content_in_port
final_cache += template_json['cache_tail']
cache_dest.write(final_cache)
cache_dest.close()
print('-------------   finish Controller -------------')

final_msg = template_json['message_header']
final_msg += murphy_parser.converIncomingMsgToFileString()
final_msg += template_json['message_tail']
msg_dest.write(final_msg)
msg_dest.close()
print('-------------   finish In Msg -------------')


dire_dest.write(template_json["dir"])
dire_dest.close()








