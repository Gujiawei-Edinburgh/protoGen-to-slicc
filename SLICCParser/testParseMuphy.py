import sys
from SLICCParser.ParseMurphy import ParseMurphy

test = ParseMurphy('MSI_Proto.m')
test.getTargetCode('I', 'I_load', '', False)