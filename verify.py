#!/bin/python2
import json, argparse, sys, re, sqlite3, cPickle, sys
import subprocess32 as subprocess

parser = argparse.ArgumentParser(description='Validate and check JSON output against a reference for SRT Assignment 3.')
parser.add_argument('reference_json', help='path to the reference json')
parser.add_argument('reference_stdout', help='path to the reference stdout')
parser.add_argument('jar', help='the jar to run')
parser.add_argument('test_jar', help='the test jar to run on')
parser.add_argument('rowid', help='rowid to update with the results')

args = parser.parse_args()

def write_and_exit(failure_message=None):
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    c.execute('UPDATE submits SET result = ? WHERE rowid = ?', (result_, args.rowid))

    if failure_message is not None:
        c.execute('INSERT INTO failure_message (submit_id, message) VALUES (?, ?)', (args.rowid, failure_message))

    conn.commit()
    conn.close()
    sys.exit(0)

def write_stats(method, pe_found, pe_missed, pe_extra, pe_dupes, lk_found, lk_missed, lk_extra):
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    c.execute('INSERT INTO sub_stats (submit_id, method, path_edges_found, path_edges_missed, path_edges_extra, path_edges_dupes, leaks_found, leaks_missed, leaks_extra) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (args.rowid, method, pe_found, pe_missed, pe_extra, pe_dupes, lk_found, lk_missed, lk_extra))
    conn.commit()
    conn.close()

# Run the jar
try:
    result_ = 'stdout:\n'
    stdout_this = subprocess.check_output('timeout 300 java -jar %s %s %s' % (args.jar, args.test_jar, args.jar + '_output.json'), shell=True, stderr=subprocess.STDOUT)
except subprocess.CalledProcessError as cpe:
    # result_ += '\nstderr:\n' + cpe.output
    result_ += 'abnormal termination'
    write_and_exit(cpe.output)

# Check the output
ref_leaks = {}
found_leaks = {}

leak_pattern = r'^Leak at \d+: \w+ \<[^>]*\>\([^)]*\) in method (\<[^>]*\>)'

with open(args.reference_stdout, 'r') as f:
    stdout_ref = f.read()

for line in stdout_ref.splitlines():
    if line.startswith('Leak at'):
        m = re.search(leak_pattern, line)
        method = m.group(1)

        if method not in ref_leaks:
            ref_leaks[method] = set()
            found_leaks[method] = set()

        ref_leaks[method].add(line)

for line in stdout_this.splitlines():
    if line.startswith('Leak at'):
        result_ += line + '\n'
        m = re.search(leak_pattern, line)
        method = m.group(1)

        if method not in found_leaks:
            found_leaks[method] = set()

        found_leaks[method].add(line)

lk_found = dict([(method, 0) for method in ref_leaks])
lk_missed = dict([(method, 0) for method in ref_leaks])
lk_extra = dict([(method, 0) for method in found_leaks])

for method in ref_leaks:
    for leak in ref_leaks[method]:
        if method in found_leaks and leak in found_leaks[method]:
            lk_found[method] += 1
        else:
            lk_missed[method] += 1

for method in found_leaks:
    for leak in found_leaks[method]:
        if method not in ref_leaks or leak not in ref_leaks[method]:
            lk_extra[method] += 1

sign_pattern = r'^\<([a-zA-Z_\$][a-zA-Z\d_\$]*\.)*[a-zA-Z_\$][a-zA-Z\d_\$]*\: ([a-zA-Z_\$][a-zA-Z\d_\$]*\.)*[a-zA-Z_\$][a-zA-Z\d_\$]* (\<)?[a-zA-Z_\$][a-zA-Z\d_\$]*(\>)?(\((([a-zA-Z_\$][a-zA-Z\d_\$]*\.)*[a-zA-Z_\$][a-zA-Z\d_\$]*(?:\[\])*, )*([a-zA-Z_\$][a-zA-Z\d_\$]*\.)*[a-zA-Z_\$][a-zA-Z\d_\$]*(?:\[\])*\)|\(\))\>$'
name_pattern = r'^([a-zA-Z_\$][a-zA-Z\d_\$]*\.)*[a-zA-Z_\$][a-zA-Z\d_\$]*$'
uidx_pattern = r'^\d+$'

result_ += '\n'
result_ += 'Validating...\n'

try:
    with open(args.jar + '_output.json', 'r+') as f:
        result = json.load(f)
except ValueError:
    result_ += 'Failed to parse JSON.' + '\n'
    write_and_exit('Failed to parse JSON')

for signature in result:
    path_edges = result[signature]
    if not re.match(sign_pattern, signature):
        result_ += signature + ' is not a valid signature' + '\n'
        write_and_exit(signature + ' is not a valid signature')

    for path_edge in path_edges:
        # unit_index
        if "unit_index" not in path_edge:
            result_ += "Each path edge must have a unit_index" + '\n'
            write_and_exit("Each path edge must have a unit_index")
        uidx_ = path_edge["unit_index"]
        if not re.match(uidx_pattern, uidx_):
            result_ += uidx_ + " is not a valid unit_index" + '\n'
            write_and_exit(uidx_ + " is not a valid unit_index")

        # source_dataflowfact
        if "source_dataflowfact" not in path_edge:
            result_ += "Each path edge must have a source_dataflowfact" + '\n'
            write_and_exit("Each path edge must have a source_dataflowfact")
        if "identifier" not in path_edge["source_dataflowfact"]:
            result_ += "Each dataflowfact must have an identifier" + '\n'
            write_and_exit("Each dataflowfact must have an identifier")
        if "type" not in path_edge["source_dataflowfact"]:
            result_ += "Each dataflowfact must have a type" + '\n'
            write_and_exit("Each dataflowfact must have a type")

        id_ = path_edge["source_dataflowfact"]["identifier"]
        typ = path_edge["source_dataflowfact"]["type"]
        if not re.match(name_pattern, id_):
            result_ += id_ + ' is not a valid identifier' + '\n'
            write_and_exit(id_ + ' is not a valid identifier')
        if not re.match(name_pattern, typ):
            result_ += typ + ' is not a valid type name' + '\n'
            write_and_exit(typ + ' is not a valid type name')

        # target_dataflowfact
        if not "target_dataflowfact" in path_edge:
            result_ += "Each path edge must have a target_dataflowfact" + '\n'
            write_and_exit("Each path edge must have a target_dataflowfact")
        if not "identifier" in path_edge["target_dataflowfact"]:
            result_ += "Each dataflowfact must have an identifier" + '\n'
            write_and_exit("Each dataflowfact must have an identifier")
        if not "type" in path_edge["target_dataflowfact"]:
            result_ += "Each dataflowfact must have a type" + '\n'
            write_and_exit("Each dataflowfact must have a type")

        id_ = path_edge["target_dataflowfact"]["identifier"]
        typ = path_edge["target_dataflowfact"]["type"]
        if not re.match(name_pattern, id_):
            result_ += id_ + ' is not a valid identifier' + '\n'
            write_and_exit(id_ + ' is not a valid identifier')
        if not re.match(name_pattern, typ):
            result_ += typ + ' is not a valid type name' + '\n'
            write_and_exit(typ + ' is not a valid type name')

result_ += 'Result: Congratulations! At least your format is correct. (Yay...)' + '\n'
result_ += '\nVerifying...' + '\n'

# Check path edges

def pe2str(path_edge):
  return '(s, ' + path_edge['source_dataflowfact']['identifier'] + ':' + path_edge['source_dataflowfact']['type']  + ') -> (' + path_edge['unit_index'] + ', ' + path_edge['target_dataflowfact']['identifier'] + ':' + path_edge['target_dataflowfact']['type']  + ')'

try:
    with open(args.reference_json, 'r+') as f:
        reference = json.load(f)
except ValueError:
    result_ += 'Failed to parse JSON.' + '\n'
    write_and_exit()

result_pe = {}
reference_pe = {}
issue = False

pe_found = {}
pe_missed = {}
pe_extra = {}
pe_dupes = {}

for signature in result:
    path_edges = result[signature]
    result_pe[signature] = set()
    pe_dupes[signature] = 0

    for path_edge in path_edges:
        path_edge = cPickle.dumps(path_edge)
        if path_edge in result_pe[signature]:
            result_ += 'Warning:' + signature + ' ' + pe2str(cPickle.loads(path_edge)) + ' reported more than once' + '\n'
            pe_dupes[signature] += 1
            issue = True

        result_pe[signature].add(path_edge)

for signature in reference:
    print '>>>', signature
    path_edges = reference[signature]
    reference_pe[signature] = set()
    pe_missed[signature] = 0
    pe_found[signature] = 0

    for path_edge in path_edges:
        path_edge = cPickle.dumps(path_edge)
        reference_pe[signature].add(path_edge)

        if signature not in result_pe or path_edge not in result_pe[signature]:
            print '::', signature
            result_ +=  signature + ' ' + pe2str(cPickle.loads(path_edge)) + ' not found' + '\n'
            pe_missed[signature] += 1
            issue = True
        else:
            pe_found[signature] += 1

for signature in result:
    pe_extra[signature] = 0
    path_edges = result[signature]

    for path_edge in path_edges:
        path_edge = cPickle.dumps(path_edge)
        if signature not in reference_pe or path_edge not in reference_pe[signature]:
            result_ +=  signature + ' ' + pe2str(cPickle.loads(path_edge)) + ' not expected, but found' + '\n'
            pe_extra[signature] += 1
            issue = True

if not issue:
    result_ += 'Result: You got it right... this time!' + '\n'
else:
    result_ += 'Result: *Ba Dam Tss* Try... again?' + '\n'

for method in reference:
    if method not in pe_found:
        pe_found[method] = 0
    if method not in pe_missed:
        pe_missed[method] = 0
    if method not in pe_extra:
        pe_extra[method] = 0
    if method not in pe_dupes:
        pe_dupes[method] = 0
    if method not in lk_found:
        lk_found[method] = 0
    if method not in lk_missed:
        lk_missed[method] = 0
    if method not in lk_extra:
        lk_extra[method] = 0

    write_stats(method, pe_found[method], pe_missed[method], pe_extra[method], pe_dupes[method], lk_found[method], lk_missed[method], lk_extra[method])

for method in found_leaks:
    if method not in ref_leaks:
        write_stats(method, 0, 0, pe_extra[method], pe_dupes[method], 0, 0, lk_extra[method])

write_and_exit()
