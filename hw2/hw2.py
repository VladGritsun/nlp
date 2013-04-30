import json

def fill_freq(tree,word_freq) :
    if len(tree) == 2 :
        if tree[1] in word_freq :
            word_freq[tree[1]] += 1
        else :
            word_freq[tree[1]] = 1
    else :
        fill_freq(tree[1],word_freq)
        fill_freq(tree[2],word_freq)

def replace_rare(tree,word_freq) :
    if len(tree) == 2 :
        if word_freq[tree[1]] < 5 :
            tree[1] = u'_RARE_'
    else :
        replace_rare(tree[1],word_freq)
        replace_rare(tree[2],word_freq)


def add_rare(file_input,file_output) :
    f_in = open(file_input)
    word_freq = {}
    for line in f_in.readlines() :
        tree = json.loads(line)
        fill_freq(tree,word_freq)
    f_in = open(file_input)
    f_out = open(file_output,"w")

    for line in f_in.readlines() :
        tree = json.loads(line)
        replace_rare(tree,word_freq)
        cur = json.dumps(tree)
        f_out.write(cur+'\n')

    f_out.close()
    f_in.close()

#add_rare("parse_train.dat","parse_train_mod.dat")

def cky(sen,nonterm,binary_rule_prob,unary_rule_prob,binary_rules,start_sym,word_freq) :
    n = len(sen)
    p = [[{} for x in range(n)] for x in range(n)]
    bp = [[{} for x in range(n)] for x in range(n)]

    for i in range(n) :
        for t in nonterm :
            if sen[i] in word_freq and word_freq[sen[i]] >= 5 :
                if (t,sen[i]) in unary_rule_prob :
                    p[i][i][t] = unary_rule_prob[(t,sen[i])]
                    #print 'pi '+str(i)+' '+str(i)+' '+ t +' = '+str(p[i][i][t])
                else :
                    p[i][i][t] = 0
            else :
                if (t,'_RARE_') in unary_rule_prob:
                    p[i][i][t] = unary_rule_prob[(t,'_RARE_')]
                    #print 'pi '+str(i)+' '+str(i)+ ' '+ t +'= '+str(p[i][i][t])
                else :
                    p[i][i][t] = 0


    for l in range(2,n+1) :
        for i in range(n-l+1) :
            j = i+l-1
            #print l,i
            for t in nonterm :
                abs_max = 0
                max_rule = None

                if t not in binary_rules :
                    continue

                for y,z in binary_rules[t] :
                    for s in range(i,j) :

                        p1,p2 = 0,0
                        if y in p[i][s] :
                            p1 = p[i][s][y]
                        if z in p[s+1][j] :
                            p2 = p[s+1][j][z]

                        cur_max = binary_rule_prob[(t,y,z)]*p1*p2
                        if cur_max >= abs_max :
                            abs_max = cur_max
                            max_rule = (y,z,s)

                p[i][j][t] = abs_max
                bp[i][j][t] = max_rule
                #if p[i][j][t] > 0 :
                #    print "pi(%i %i %s) = %f" % (i+1,j+1,t,p[i][j][t])

    tree = form_parse_tree(sen,bp,start_sym,0,n-1)
    #print tree
    return tree


def form_parse_tree(sen,bp,start,i,j) :
    if i == j :
        return [start,sen[i]]
    tree = []
    y,z,s = bp[i][j][start]
    tree.append(start)
    tree.append(form_parse_tree(sen,bp,y,i,s))
    tree.append(form_parse_tree(sen,bp,z,s+1,j))
    return tree



def parse(input_file_name,output_file_name,count_file_name) :
    f_count = open(count_file_name)
    #root_symbol = "SBARQ"

    nonterm = {}
    binary_rule_prob = {}
    unary_rule_prob = {}
    binary_rules = {}
    word_freq = {}

    for line in f_count.readlines() :
        words = line.split(' ')
        words = [x.strip() for x in words]
        if words[1] == 'NONTERMINAL' :
            nonterm[words[2]] = float(words[0])
        elif  words[1] == 'BINARYRULE':
            binary_rule_prob[(words[2],words[3],words[4])] = float(words[0])
            if words[2] in binary_rules :
                binary_rules[words[2]].add((words[3],words[4]))
            else :
                binary_rules[words[2]] = set()
                binary_rules[words[2]].add((words[3],words[4]))
        else:
            unary_rule_prob[(words[2],words[3])] = float(words[0])
            if words[3] in word_freq :
                word_freq[words[3]] += float(words[0])
            else :
                word_freq[words[3]] = float(words[0])

    for x,y,z in binary_rule_prob :
        binary_rule_prob[(x,y,z)] /= nonterm[x]

    for x,w in unary_rule_prob :
        unary_rule_prob[(x,w)] /= nonterm[x]

    f_in = open(input_file_name)
    f_out = open(output_file_name,"w")

    #tree = cky(['What', 'are', 'geckos', '?'],nonterm,binary_rule_prob,unary_rule_prob,binary_rules,"SBARQ",word_freq)
    #return

    for line in f_in.readlines() :
        sen = line.split(' ')
        sen = [x.strip() for x in sen]
        start_sym = None
        if sen[-1] == '?' :
            start_sym = "SBARQ"
        else :
            start_sym = "S"

        tree = cky(sen,nonterm,binary_rule_prob,unary_rule_prob,binary_rules,start_sym,word_freq)
        f_out.write(json.dumps(tree)+'\n')
        print tree


    f_out.close()
    f_in.close()
    f_count.close()

parse("parse_test.dat","parse_test.p2.out","parse_train.counts.out")