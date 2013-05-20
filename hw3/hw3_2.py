
def eval_params(file_name_eng, file_name_for, t_params_file) :
    f_eng = open(file_name_eng)
    f_for = open(file_name_for)

    t = read_params(t_params_file)
    q = {}
    count = {}
    count_uni = {}
    count_q = {}
    count_q_tri = {}
    corpus = []

    line_count = 0

    for se, sf in zip(f_eng.readlines(),f_for.readlines()) :
        le = se.split(' ')
        le.append('_NULL_')
        l = len(le)
        for j,x in enumerate(le) :
            x = x.strip()
            lf = sf.split(' ')
            m = len(lf)
            for i,y in enumerate(lf) :
                y = y.strip()
                if j not in q :
                    q[j] = {}
                if i not in q[j] :
                    q[j][i] = {}
                if l not in q[j][i] :
                    q[j][i][l] = {}

                q[j][i][l][m] = 1.0/l

        corpus.append((se,sf))
        line_count+=1

    #for j in q :
    #    for i in q[i] :
    #        for l in q[j][i] :
    #            for m in q[j][i][l] :
                    #if j == l-1:
                    #    print 'q({}|{},{},{})={}'.format(0,i+1,l-1,m,q[j][i][l][m])
                    #else:
                    #    print 'q({}|{},{},{})={}'.format(j+1,i+1,l-1,m,q[j][i][l][m])

    print "T params"
    print

    for iter in range(5) :
        count.clear()
        count_uni.clear()
        k=1.0
        for se,sf in corpus :
            print str(iter+1)," Another line...",str(k/line_count*100)
            lf = [x.strip() for x in sf.split(' ')]
            le = [x.strip() for x in se.split(' ')]
            le.append('_NULL_')
            m = len(lf)
            l = len(le)
            for i in range(len(lf)) :
                for j in range(len(le)) :
                    cur_sum = 0
                    for x in range(len(le)) :
                        cur_q = 0
                        if x in q and i in q[j] and l in q[x][i] and m in q[x][i][l] :
                            cur_q = q[x][i][l][m]
                        cur_sum+=t[lf[i]][le[x]]*cur_q

                    cur_q = 0
                    if j in q and i in q[j] and l in q[j][i] and m in q[j][i][l] :
                        cur_q = q[j][i][l][m]

                    g = t[lf[i]][le[j]]*cur_q/cur_sum

                    #if j==(l-1) :
                    #    print "delta[{}][{}][{}]={}".format(k,i+1,0,g)
                    #else :
                    #    print "delta[{}][{}][{}]={}".format(k,i+1,j+1,g)

                    if le[j] not in count : count[le[j]] = {}
                    if lf[i] in count[le[j]] : count[le[j]][lf[i]] += g
                    else : count[le[j]][lf[i]] = g

                    if le[j] in count_uni : count_uni[le[j]] += g
                    else : count_uni[le[j]] = g

                    if j not in count_q : count_q[j] = {}
                    if i not in count_q[j] : count_q[j][i] = {}
                    if l not in count_q[j][i] : count_q[j][i][l] = {}

                    if m not in count_q[j][i][l] : count_q[j][i][l][m] = g
                    else : count_q[j][i][l][m] += g

                    if i not in count_q_tri : count_q_tri[i] = {}
                    if l not in count_q_tri[i] : count_q_tri[i][l] = {}
                    if m not in count_q_tri[i][l] : count_q_tri[i][l][m] = g
                    else : count_q_tri[i][l][m] += g

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
        #        print "t({}|{})={}".format(f,e,t[f][e])

        for j in q :
            for i in q[j] :
                for l in q[j][i] :
                    for m in q[j][i][l] :
                        q[j][i][l][m] = count_q[j][i][l][m]/count_q_tri[i][l][m]
        #                print "q({}|{},{},{})={}".format(j,i,l,m,q[j][i][l][m])

        print
        print

    f_eng.close()
    f_for.close()
    return t,q

def find_alignments(name_in_en, name_in_for, name_out, params,dist) :
    f_in_en = open(name_in_en)
    f_in_for = open(name_in_for)
    f_out = open(name_out,"w")

    for k, (se,sf) in enumerate(zip(f_in_en,f_in_for)) :
        le = [x.strip() for x in se.split(' ')]
        le.append('_NULL_')
        lf = [x.strip() for x in sf.split(' ')]
        l = len(le)
        m = len(lf)
        for i,f in enumerate(lf) :
            best_index = 0
            best_res = 0
            for j,e in enumerate(le) :
                if params[f][e]*dist[j][i][l][m] > best_res :
                    best_res = params[f][e]*dist[j][i][l][m]
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

def write_dist(f_name,dist) :
    f = open(f_name,"w")
    for j in q :
        for i in q[j] :
            for l in q[j][i] :
                for m in q[j][i][l] :
                    f.write( "{} {} {} {} {}\n".format(j,i,l,m,q[j][i][l][m]))
    f.close

def read_dist(f_name) :
    f = open(f_name,"w")
    q = {}
    for line in f.readlines():
        j,i,l,m,val = line.split(' ')
        j,i,l,m,val = int(j),int(i),int(l),int(m),int(val)
        if j not in q :
            q[j] = {}
        if i not in q[j] :
            q[j][i] = {}
        if l not in q[j][i] :
            q[j][i][l] = {}
        q[j][i][l][m] = val

    f.close
    return q

t,q = eval_params("corpus.en","corpus.es","params.out")
write_dist("dist.out",q)
#write_params("params.out",t)
#t = read_params("params.out")
find_alignments("test.en","test.es","alignment_test.p2.out",t,q)