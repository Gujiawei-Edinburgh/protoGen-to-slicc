from Algorithm.ProtoAlgorithm import *
class ProtoGenParser(ProtoAlgorithm):
    def _ProcessArch(self):

        pheader("Caches")
        pdebug(list(self.cacheIds))

        pheader("Directories")
        pdebug(list(self.dirIds))

        # First process the caches
        for arch in self.cacheIds:
            talgo = time.time()
            pheader("Architecture: " + arch)

            stablestates = self.stableStates[arch]
            statesets = self._InputProcessing(arch, stablestates)
            traces = self._AssignStateSets(arch, statesets, stablestates)

            self._FindProgressMessages(statesets)
            self._FindHiddenProgessMessages(statesets)

            self.renamedMessages.update(self._ProcessRemoteRequests(statesets, traces))

            self._ProtoGenAlgorithm(statesets, stablestates, self.maxNestingDepthCC, self._CacheDefer)

            self._AssignAccess(statesets, stablestates)

            self._MergeStates(statesets)

            pdebug("Runtime: " + arch + " = " + str(time.time() - talgo))

            statedict = self._ExtractStatesFromSets(statesets)

            self.cache_state_transitions = self._pTransitions(arch, statedict)

            self.cacheStateSets += list(statesets.values())

            self.archProtoGen.update({arch: statedict})
            pdebug("")

        for arch in self.dirIds:
            talgo = time.time()
            pheader("Architecture: " + arch)

            stablestates = self.stableStates[arch]
            statesets = self._InputProcessing(arch, stablestates)
            self._AssignStateSets(arch, statesets, stablestates)

            self._ProcessRequestsMessages(self.renamedMessages, statesets)
            self._CompleteTransitions(self.cacheStateSets, statesets)

            self._ProtoGenAlgorithm(statesets, stablestates, self.maxNestingDepthDC, self._DirectoryDefer)

            self._MergeStates(statesets)

            pdebug("Runtime: " + arch + " = " + str(time.time() - talgo))

            statedict = self._ExtractStatesFromSets(statesets)

            self.dir_state_transitions = self._pTransitions(arch, statedict)

            self.archProtoGen.update({arch: statedict})
            pdebug("")
        

    def _pTransitions(self, arch, statedict):
        transitions = self._pGetTransitions(statedict)
        pheader(arch + ": Total number of transitions: " + str(len(transitions)))
        ProtoCCTablePrinter().ptransitiontable(transitions)
        return transitions
    
    def getCacheTransitions(self):
        return self.cache_state_transitions
    
    def getDirTransitions(self):
        return self.dir_state_transitions