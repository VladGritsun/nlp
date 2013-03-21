import os
from collections import defaultdict

def add_rare(in_file,out_file) :
    f_in = open(in_file)
    word_freq = {}
    for line in f_in.readlines() :
        sline = line.split(' ')
        if sline[0] in word_freq :
            word_freq[sline[0]] += 1
        else :
            word_freq[sline[0]] = 1
    f_in.close()
    f_in = open(in_file)
    f_out = open(out_file,'w')
    for line in f_in.readlines( ) :
        if line == '\n' :
            f_out.write(line)
            continue
        sline = line.split(' ')
        if word_freq[sline[0]] < 5:
            cur_line = '_RARE_ '+sline[1]
            #line.replace(sline[0], '_RARE_')
            f_out.writelines([cur_line])
        else :
            f_out.write(line)

    f_in.close()
    f_out.close()

def eval_tags(count_file):
    f = open(count_file)
    tag_table = set()

    for line in f :
        sline = line.split()
        if len(sline) > 1 and sline[1]=='1-GRAM' :
            tag_table.add(sline[2])

    f.close()
    return tag_table

def eval_emission(count_file):
    f = open(count_file)
    tag_counter = {}
    emission_table = {}
    for line in f :
        sline = line.split()
        if len(sline) > 1 and sline[1]=='1-GRAM' :
            tag_counter[sline[2]] = int(sline[0])

    f = open(count_file)
    for line in f :
        sline = line.split()
        if len(sline)>1 and sline[1]=='WORDTAG' :
            cur_val = float(sline[0])/tag_counter[sline[2]]
            if sline[3] in emission_table :
                emission_table[sline[3]].append((cur_val,sline[2]))
            else :
                emission_table[sline[3]] = [(cur_val,sline[2])]

    f.close()
    return emission_table

def eval_emission_mod(count_file):
    f = open(count_file)
    tag_counter = {}
    emission_table = {}
    for line in f :
        sline = line.split()
        if len(sline) > 1 and sline[1]=='1-GRAM' :
            tag_counter[sline[2]] = int(sline[0])

    f = open(count_file)
    for line in f :
        sline = line.split()
        if len(sline)>1 and sline[1]=='WORDTAG' :
            cur_val = float(sline[0])/tag_counter[sline[2]]
            emission_table[(sline[3],sline[2])] = cur_val

    f.close()
    return emission_table


def eval_trigram(count_file) :
    f = open(count_file)
    bigram_table = {}
    trigram_table = {}
    for x in f.readlines() :
        xs = x.split()
        if len(xs)>1:
            if xs[1]=='2-GRAM' :
                bigram_table[(xs[2],xs[3])] = float(xs[0])
            elif xs[1]=='3-GRAM':
                trigram_table[(xs[2],xs[3],xs[4])] = float(xs[0])

    for x in trigram_table :
        ypp,yp,y = x
        trigram_table[x] /= bigram_table[(ypp,yp)]
        print str(x)+' '+str(trigram_table[x])

    f.close()
    return trigram_table

def tagger(in_file,out_file,count_file) :
    emit_table = eval_emission(count_file)
    f_in = open(in_file)
    f_out = open(out_file,'w')

    for line in f_in :
        if line=='\n':
            f_out.write(line)
            continue
        pr,tag = 0,''
        if line.strip() not in emit_table :
            pr,tag = max(emit_table['_RARE_'])
        else:
            pr,tag = max(emit_table[line.strip()])
        cur_line = line.strip()+' '+tag+'\n'
        f_out.write(cur_line)

    f_in.close()
    f_out.close()

def get_sentence(file) :
    cur = []
    for x in file.readlines() :
        if x=='\n':
            yield cur
            cur = []
            continue
        x = x.strip()
        cur.append(x)

def viterbi(sent,tag_table,emit_table,trig_table,get_tags,pad) :
    p = {}
    bp = {}
    for k in range(0,len(sent)+1) :
        p[k] = {}
        bp[k] = {}
        for u in get_tags(k-1) :
            p[k][u] = {}
            bp[k][u] = {}
            for v in get_tags(k) :
                p[k][u][v] = 0
                bp[k][u][v] = ''
    p[0]['*']['*'] = 1

    for k in range(1,len(sent)+1) :
        for u in get_tags(k-1) :
            for v in get_tags(k) :
                val_max = None
                arg_max = None
                emit_val = None
                if (sent[k-1],v) in emit_table :
                    emit_val = emit_table[(sent[k-1],v)]
                else :
                    for x in tag_table :
                        if (sent[k-1],x) in emit_table :
                            emit_val = 0
                            break
                    else :
                        emit_val = emit_table[('_RARE_',v)]
                    #emit_val = emit_table[('_RARE_',v)]
                    #emit_val = 0
                for w in get_tags(k-2) :
                    cur_max = p[k-1][w][u]*trig_table[(w,u,v)]*emit_val
                    if val_max == None or cur_max > val_max :
                        val_max = cur_max
                        arg_max = w
                p[k][u][v] = val_max
                print 'PI('+str(k)+','+u+','+v+')='+str(val_max)
                bp[k][u][v] = arg_max

    n = len(sent)
    tags = ['']*n
    val_max = None
    for u in get_tags(n-1) :
        for v in get_tags(n) :
            cur_max = p[n][u][v]*trig_table[(u,v,'STOP')]
            if val_max==None or cur_max > val_max :
                val_max = cur_max
                tags[n-2] = u
                tags[n-1] = v
    for k in range(n-2,0,-1) :
        tags[k-1] = bp[k+2][tags[k]][tags[k+1]]

    print tags

    return tags

def tagger_impr(in_file,out_file,count_file):
    pad = set()
    pad.add('*')
    tag_table = eval_tags(count_file)
    emit_table = eval_emission_mod(count_file)
    trig_table = eval_trigram(count_file)
    get_tags = lambda k: pad if k == -1 or k == 0  else tag_table

    f_in = open(in_file)
    f_out = open(out_file,'w')

    for sent in get_sentence(f_in) :
        tags = viterbi(sent,tag_table,emit_table,trig_table,get_tags,pad)
        for k in range(len(sent)):
            cur_line = sent[k].strip()+' '+tags[k]+'\n'
            f_out.write(cur_line)
        f_out.write('\n')

    f_in.close()
    f_out.close()

tagger_impr('sample.dev','gene_dev.p1.out','gene_mod.counts')

