
def eval_params(file_name_eng, file_name_for) :
    f_eng = open(file_name_eng)
    f_for = open(file_name_for)

    t = {}
    count = {}
    count_uni = {}
    corpus = []
    eng_poss_transl = {}
    eng_poss_transl['_NULL_'] = set()

    for se, sf in zip(f_eng.readlines(),f_for.readlines()) :
        for x in se.split(' ') :
            x = x.strip()
            if x not in eng_poss_transl :
                eng_poss_transl[x] = set()
            for y in sf.split(' ') :
                y = y.strip()
                eng_poss_transl[x].add(y)

        for x in sf.split(' ') :
            x = x.strip()
            eng_poss_transl['_NULL_'].add(x)

        corpus.append((se,sf))

    for x in eng_poss_transl :
        print 'n({})={}'.format(x,len(eng_poss_transl[x]))

    print
    print "T params"

    for se,sf in corpus :
        print "0 Another line..."
        le = se.split(' ')
        le = [x.strip() for x in le]
        le.append('_NULL_')
        for e in le:
            for f in sf.split(' ') :
                f = f.strip()
                if f not in t : t[f] = {}
                t[f][e] = 1.0/len(eng_poss_transl[e])
                #print "p({}|{})={}".format(f,e,t[f][e])

    print
    print

    for iter in range(2) :
        count = {}
        count_uni = {}
        k=1
        for se,sf in corpus :
            print str(iter+1)," Another line..."
            lf = [x.strip() for x in sf.split(' ')]
            le = [x.strip() for x in se.split(' ')]
            le.append('_NULL_')
            for i in range(len(lf)) :
                for j in range(len(le)) :
                    cur_sum = 0
                    for x in range(len(le)) : cur_sum+=t[lf[i]][le[x]]
                    g = t[lf[i]][le[j]]/cur_sum
                    #print "delta[{}][{}][{}]={}".format(k,i+1,j,g)

                    if le[j] not in count : count[le[j]] = {}

                    if lf[i] in count[le[j]] : count[le[j]][lf[i]] += g
                    else : count[le[j]][lf[i]] = g
                    if le[j] in count_uni : count_uni[le[j]] += g
                    else : count_uni[le[j]] = g
            k+=1

        print
        print

        #for cnt1 in count :
        #    for cnt2 in count[cnt1] :
        #        print "c({},{})={}".format(cnt1,cnt2 ,count[cnt1][cnt2])
        #for cnt in count_uni : print "c({})={}".format(cnt,count_uni[cnt])
        #print
        #print

        for f in t :
            for e in t[f]:
                t[f][e] = count[e][f]/count_uni[e]
                #print "t({}|{})={}".format(f,e,t[f][e])

        print
        print

    f_eng.close()
    f_for.close()
    return t

def find_alignments(name_in_en, name_in_for, name_out, params) :
    f_in_en = open(name_in_en)
    f_in_for = open(name_in_for)
    f_out = open(name_out,"w")

    for k, (se,sf) in enumerate(zip(f_in_en,f_in_for)) :
        le = [x.strip() for x in se.split(' ')]

        le.append('_NULL_')
        lf = [x.strip() for x in sf.split(' ')]
        for i,f in enumerate(lf) :
            best_index = 0
            best_res = 0
            for j,e in enumerate(le) :
                if params[f][e] > best_res :
                    best_res = params[f][e]
                    best_index = j
            if best_index == len(le)-1 :
                s = "{} {} {}\n".format(k+1, 0, i+1)
                f_out.write(s)
                print s
            else :
                s = "{} {} {}\n".format(k+1, best_index+1, i+1)
                f_out.write(s)
                print s

    f_in_en.close()
    f_in_for.close()
    f_out.close()

def write_params(file_name,params) :
    file = open(file_name,"w")
    for f in params :
        for e in params[f] :
            file.write("{} {} {}\n".format(f,e,params[f][e]))
    file.close()

def read_params(file_name) :
    file = open(file_name)
    t = {}
    for line in file.readlines() :
        f,e,val = line.split(' ')
        if f not in t :
            t[f] = {}
        t[f][e] = float(val)
    file.close()
    return t

t = eval_params("debug.en","debug.es")
write_params("debug.par",t)
#t = read_params("params.out")
find_alignments("debug.en","debug.es","debug.out",t)