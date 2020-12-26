class ParseMurphy:

    def __init__(self, file_name):
        self.output_file_name = file_name.replace('pcc', 'm')
        self.file = None
        self.stable_states = set()
        self.forward_msg = set()
        self.resp_msg = set()
        self.incomingMsg = set()
    

    def getTargetCode(self, start_state, final_state, condition, is_mandatory, event): 
        parseCondition = None   
        if condition:
            parseCondition = self.getIfBlockStatement(condition)
        self.file = open(self.output_file_name, encoding='utf-8')
        line = self.file.readline()
        while line:
            if line.__contains__('Func_cache'):
                while line:
                    if line.__contains__('case cache_'+start_state):
                        while line:
                            if line.__contains__('case '+event):
                                if parseCondition:
                                    result_message = {}
                                    line = self.file.readline()
                                    if line.__contains__('cle.acksExpected := inmsg.acksExpected'):
                                        result_message['ack'] = 'storeAcks'
                                    elif line.__contains__:
                                        pass
                                    print('if-else statement is unclear and deal with it later')
                                else:
                                    result_message = {}
                                    while line:
                                        if line.__contains__('cle.Perm := store') or line.__contains__('cle.Perm := load'):
                                            tempLine = line.strip()
                                            result_message['permision'] = tempLine.split(' ')[-1].replace(';', '')
                                        elif line.__contains__('i_cache_Defermsg'):
                                            result_message['stall'] = 'stall'
                                        elif line.__contains__('cle.cl := inmsg.cl;'):
                                            result_message['data'] = True
                                        elif line.__contains__('cle.acksReceived := cle.acksReceived+1'):
                                            result_message['ack'] = 'decrAcks'
                                        elif line.__contains__('cle.acksExpected := inmsg.acksExpected;'):
                                            result_message['ack'] = 'storeAcks'
                                        elif (line.__contains__('case') or line.__contains__('else return false')):
                                            break
                                        line = self.file.readline()
                                    return 1, result_message
                            line = self.file.readline()
                    line = self.file.readline()
                return -1, 'next part'
            elif (not is_mandatory) and line.__contains__('SEND_cache_'+start_state+'_'+event):
                while line and not line is '\n':
                    if line.__contains__('cle.Perm := store') or line.__contains__('cle.Perm := load'):
                        return 0, 'Hit'
                    line = self.file.readline()
                return 0, 'Miss'
            line = self.file.readline()
        return -2, 'unknown part'

    def getStableStates(self, state_transitions):
        for each in state_transitions:
            start_state = each.getstartstate().getstatename()
            if len(start_state) == 1 and not self.stable_states.__contains__(start_state):
                self.stable_states.add(start_state)
        return 
    

    def getIfBlockStatement(self, condition):
        if not condition:
            return None
        else:
            conditionTemp = condition[0]
            if conditionTemp == 'NCOND_acksExpected==acksReceived':
                return 'else'
            elif conditionTemp == 'COND_acksExpected==acksReceived':
                return 'cle.acksExpected=cle.acksReceived'


    def getMessageType(self, transitions):
        for each_transition in transitions:
            in_msg = None
            if isinstance(each_transition.inMsg, str):
                in_msg = each_transition.inMsg
                if in_msg != '':
                    self.forward_msg.add(in_msg)
            else:
                in_msg = each_transition.getinmsg().getmsgtype()
                self.resp_msg.add(in_msg)
        return


    def writeActionsBlocks(self, destination, transitions):
        for each_transition in transitions:
            if each_transition.outMsg:
                for each_out_Msg in each_transition.outMsg:
                    content = 'action(send' + each_out_Msg.type + '){\n'
                    if each_out_Msg.type in self.resp_msg:
                        content = content + '\t' + 'peek(forward_in, RequestMsg) {\n'
                        content = content + '\t\t' + 'enqueue(response_out, RequestMsg, 1) {\n'
                        content = content + '\t\t\t' + 'out_msg.addr := address;\n'
                        content = content + '\t\t\t' + 'out_msg.Type := CoherenceRequestType:' + each_out_Msg.type + ';\n'
                        content = content + '\t\t\t' + 'out_msg.Destination.add(in_msg.Requestor);\n'
                        content = content + '\t\t\t' + 'out_msg.DataBlk := cache_entry.DataBlk;\n'
                        content = content + '\t\t\t' + 'out_msg.MessageSize := MessageSizeType:Data;\n'
                        content = content + '\t\t\t' + 'out_msg.Sender := machineID;\n'
                        content = content + '\t\t' + '}\n'
                        content = content + '\t' + '}\n'
                        content = content + '}' + '\n' + '\n'
                    elif each_out_Msg.vc == 'req':
                        content = content + '\t' + 'enqueue(request_out, RequestMsg, 1) {\n'
                        content = content + '\t\t' + 'out_msg.addr := address;\n'
                        content = content + '\t\t' + 'out_msg.Type := CoherenceRequestType:' + each_out_Msg.type + ';\n'
                        content = content + '\t\t' + 'out_msg.Destination.add(mapAddressToMachine(address,MachineType:Directory));\n'
                        content = content + '\t\t' + 'out_msg.DataBlk := cache_entry.DataBlk;\n'
                        content = content + '\t\t' + 'out_msg.MessageSize := MessageSizeType:Data;\n'
                        content = content + '\t\t' + 'out_msg.Requestor := machineID;\n'
                        content = content + '\t' + '}\n'
                        content = content + '}' + '\n' + '\n'
                    elif each_out_Msg.vc == 'resp':
                        content = content + '\t' + 'enqueue(response_out, RequestMsg, 1) {\n'
                        content = content + '\t\t' + 'out_msg.addr := address;\n'
                        content = content + '\t\t' + 'out_msg.Type := CoherenceRequestType:' + each_out_Msg.type + ';\n'
                        content = content + '\t\t' + 'out_msg.Destination.add(mapAddressToMachine(address,MachineType:Directory));\n'
                        content = content + '\t\t' + 'out_msg.DataBlk := cache_entry.DataBlk;\n'
                        content = content + '\t\t' + 'out_msg.MessageSize := MessageSizeType:Data;\n'
                        content = content + '\t\t' + 'out_msg.Sender := machineID;\n'
                        content = content + '\t' + '}\n'
                        content = content + '}' + '\n' + '\n'
                destination.write(content)
        return 


    def getMappingTransition(self, transitions):
        transition_mapping = {}
        for each in transitions:
            start_state = each.getstartstate().getstatename()
            final_state = each.getfinalstate().getstatename()
            in_msg = each.getinmsg()
            if not isinstance(in_msg, str):
                in_msg = in_msg.getmsgtype()
            
            self.incomingMsg.add(in_msg)
            condition = each.getcond()
            out_msg = each.getoutmsg()
            access = each.access
            if start_state in transition_mapping:
                listTemp = transition_mapping[start_state]
                is_in_msg_exist = False
                for eachTransition in listTemp:
                    if in_msg == eachTransition['in_msg']:
                        eachTransitionTemp = eachTransition['transition']
                        eachTransitionTemp.append({'out_msg':out_msg, 'final_state':final_state, 'condition':condition, 'access':access})
                        is_in_msg_exist = True
                        break
                if is_in_msg_exist is False:
                    eachTransition = {}
                    eachTransition['in_msg'] = in_msg
                    eachTransition['transition'] = [{'out_msg':out_msg, 'final_state':final_state, 'condition':condition, 'access':access}]
                    listTemp.append(eachTransition)
                transition_mapping[start_state] = listTemp
            else:
                listTemp = []
                eachTransition = {}
                eachTransition['in_msg'] = in_msg
                eachTransition['transition'] = [{'out_msg':out_msg, 'final_state':final_state, 'condition':condition, 'access':access}]
                listTemp.append(eachTransition)
                transition_mapping[start_state] = listTemp
        return transition_mapping



    def getCacheFuncTargetCode(self, start_state, transition, in_msg):
        result_message = {}
        if len(transition) == 2:     #there are two cases i.e. equals or not equals
            result_message['reg'] = {}
        
        self.file = open(self.output_file_name, encoding='utf-8')
        line = self.file.readline()
        while line:
            if line.__contains__('Func_cache'):
                while line:
                    if line.__contains__('case cache_'+start_state):
                        while line:
                            if line.__contains__('case '+in_msg):
                                if len(transition) == 2:
                                    line = self.file.readline()
                                    if line.__contains__('+'):
                                        result_message['reg'] = 'entry.acksReceivedL1 := entry.acksReceivedL1+1;'
                                    else:
                                        tempContent = 'entry.acksExpectedL1 := in_msg.acksExpected;\n'
                                        tempContent = tempContent + '\t\t\t\t\t' + 'entry.clL1 := in_msg.cl;'
                                        result_message['reg'] = tempContent
                                    return 1, result_message
                                elif len(transition) == 1:
                                    line = self.file.readline()
                                    while line:
                                        if line.__contains__('cle.cl := inmsg.cl;'):
                                            result_message['data'] = 'entry.clL1 := in_msg.cl;'
                                        if line.__contains__('cle.acksReceived := cle.acksReceived+1'):
                                            result_message['ack'] = 'entry.acksReceivedL1 := entry.acksReceivedL1+1;'
                                        if line.__contains__('cle.acksExpected := inmsg.acksExpected;'):
                                            result_message['ack'] = 'entry.acksExpectedL1 := in_msg.acksExpected;'
                                        if line.__contains__('else return false') or line.__contains__('case'):
                                            break
                                        line = self.file.readline()
                                    return 1, result_message
                            line = self.file.readline()
                    line = self.file.readline()
                return -1, 'next part'
            line = self.file.readline()
        return -1, 'unknown part'


    def getStateTransitionPart(self, in_msg, final_state, each_transition):
        content = '\t\t\t\t\t' + 'setState(tbe, entry, LineAddress, State:' + final_state + ');\n'
        if len(final_state) == 1:  #final state is a stable state
            content = content + '\t\t\t\t\t' + 'assert(is_valid(entry));\n'
            if final_state == 'I':
                content = content + '\t\t\t\t\t' + 'trigger(Event:deallocfwdfrom_in, LineAddress, entry, tbe);\n'
            else:
                operationCallBack = ''
                if in_msg.__contains__('M') or in_msg.__contains__('Inv_Ack'):
                    operationCallBack = 'writeCallback'
                elif in_msg.__contains__('S'):
                    operationCallBack = 'readCallback'
                content += '\t' * 5 + 'cache.setMRU(entry);\n'
                content = content + '\t\t\t\t\t' + 'sequencer.' + operationCallBack + '(LineAddress, entry.clL1, true, machineIDToMachineType(in_msg.Sender));\n' + '\t'*5 +'fwdfrom_in.dequeue(clockEdge());\n'
        else:  # final state is a transient state
            content = content + '\t\t\t\t\t' + 'fwdfrom_in.dequeue(clockEdge());\n'
        #deal with output messages
        out_msg = each_transition['out_msg']
        if out_msg is not None or len(out_msg) != 0:
            for each in out_msg:
                content = content + '\t\t\t\t\t' + 'enqueue(' + each.vc + 'to_out, CoherenceMessage, responseLatency) {\n'
                content = content + '\t\t\t\t\t\t' + 'out_msg.LineAddress := LineAddress;\n'
                content = content + '\t\t\t\t\t\t' + 'out_msg.MessageSize := MessageSizeType:Data;\n'
                if str(each.dest).__contains__('directory'):
                    content += '\t' * 6 + 'out_msg.Destination.add(mapAddressToMachine(LineAddress, MachineType:Directory));\n'
                else:
                    content = content + '\t\t\t\t\t\t' + 'out_msg.Destination.add(in_msg.Sender);\n'
                content = content + '\t\t\t\t\t\t' + 'out_msg.Type := CoherenceMessageType:' + each.type + ';\n'
                content = content + '\t\t\t\t\t\t' + 'out_msg.Sender := machineID;\n'
                content = content + '\t\t\t\t\t\t' + 'out_msg.cl := entry.clL1;\n'
                content = content + '\t\t\t\t\t' + '}\n'
        return content


    def getStateMandatoryPart(self, final_state, out_msg):
        content = ''
        for each in out_msg:
            content += '\t' * 5 + 'enqueue(reqto_out, CoherenceMessage, responseLatency) {\n'
            content += '\t' * 6 + 'out_msg.LineAddress := LineAddress;\n'
            content += '\t' * 6 + 'out_msg.MessageSize := MessageSizeType:Data;\n'
            content += '\t' * 6 + 'out_msg.Destination.add(mapAddressToMachine(LineAddress, MachineType:Directory));\n'
            content += '\t' * 6 + 'out_msg.Type := CoherenceMessageType:PutM;\n'
            content += '\t' * 6 + 'out_msg.Sender := machineID;\n'
            content += '\t' * 6 + 'out_msg.cl := entry.clL1;\n'
            content += '\t' * 5 + '}\n'
        
        content += '\t' * 5 + 'setState(tbe, entry, LineAddress, State:M_evict);\n'
        content += '\t' * 5 + 'if (send_evictions) {\n'
        content += '\t' * 6 + 'sequencer.evictionCallback(LineAddress);\n'
        content += '\t' * 5 + '}\n'
        return content

    def converIncomingMsgToFileString(self):
        content = ''
        for eachMsg in self.incomingMsg:
            if len(str(eachMsg)) == 0:
                continue
            content += str(eachMsg) + ',\t' + 'desc="... TODO ...";\n'
        return content


