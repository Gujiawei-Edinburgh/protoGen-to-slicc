# protoGen_to_slicc
This is a projrct of parsing outcome of protoGen to slicc for further analysis such as performance test.
As we all know, resoning the whole process of concurrent cache coherence process is hard, e.g. MESI and MSI. Therefore, protoGen solves this
problem. It can generate the protocol with high concurrency. Also, the outcome of protoGen is written by murphy that is used for model checking,
In order to test the generated protocol performance, it should be converted into SLICC. That is what the project serves. It is somehow a complier.

To run the complier, we shoule simply type `python3 generator.py`in command line. The default env is python3. Also, othe depencies can be find in the repository [protoGen](https://github.com/icsa-caps/ProtoGen)
