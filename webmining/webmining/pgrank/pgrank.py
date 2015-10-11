from webmining.pages.models import Link,Page,SearchTerm

num_iterations = 100
D = 0.85
def pgrank(searchid):
    s = SearchTerm.objects.get(id=int(searchid))
    links = s.links.all()
    print 'len',len(links),' name',s.term
    from_ids = [i.from_id for i in links ]
    # Find the ids that receive page rank 
    links_received = []
    to_ids = []
    for l in links:
        from_id = l.from_id
        to_id = l.to_id
        if from_id not in from_ids: continue
        if to_id  not in from_ids: continue
        links_received.append([from_id,to_id])
        if to_id  not in to_ids: to_ids.append(to_id)
        
    pages = s.pages.all()
    prev_ranks = dict()
    for node in from_ids:
        ptmp  = Page.objects.get(id=node)
        prev_ranks[node] = ptmp.old_rank
        
    print 'prev_ranks:',len(prev_ranks)
    for i in range(num_iterations):
        next_ranks = dict()
        total = 0.0
        for (node,old_rank) in prev_ranks.items():
            total += old_rank
            next_ranks[node] = 0.0
        
        #find the outbound links and send the pagerank down to each of them
        for (node, old_rank) in prev_ranks.items():
            give_ids = []
            for (from_id, to_id) in links_received:
                if from_id != node: continue
                if to_id  not in to_ids: continue
                give_ids.append(to_id)
            if (len(give_ids) < 1): continue
            amount = D*old_rank/len(give_ids)
            for id in give_ids:
                next_ranks[id] += amount
        newtot = 0
        for (node,next_rank) in next_ranks.items():
            newtot += next_rank
        const = (1-D)/ len(next_ranks)
        
        for node in next_ranks:
            next_ranks[node] += const
        
        newtot = 0
        for (node,old_rank) in next_ranks.items():
            newtot += next_rank
        
        difftot = 0
        for (node, old_rank) in prev_ranks.items():
            new_rank = next_ranks[node]
            diff = abs(old_rank-new_rank)
            difftot += diff
        
        #diff_av = difftot/len(prev_ranks)
        prev_ranks = next_ranks
        
    for (id,new_rank) in next_ranks.items():
        ptmp = Page.objects.get(id=id)
        url = ptmp.url
        print id,' url:',url
    
    for (id,new_rank) in next_ranks.items():
        ptmp = Page.objects.get(id=id)
        ptmp.old_rank = new_rank
        ptmp.new_rank = new_rank
        ptmp.save()

'''
def pagerank(graph, damping=0.85, epsilon=1.0e-8):
    inlink_map = {}
    outlink_counts = {}
    
    def new_node(node):
        if node not in inlink_map: inlink_map[node] = set()
        if node not in outlink_counts: outlink_counts[node] = 0
    
    for tail_node, head_node in graph:
        new_node(tail_node)
        new_node(head_node)
        if tail_node == head_node: continue
        
        if tail_node not in inlink_map[head_node]:
            inlink_map[head_node].add(tail_node)
            outlink_counts[tail_node] += 1
    
    all_nodes = set(inlink_map.keys())
    for node, outlink_count in outlink_counts.items():
        if outlink_count == 0:
            outlink_counts[node] = len(all_nodes)
            for l_node in all_nodes: inlink_map[l_node].add(node)
    
    initial_value = 1 / len(all_nodes)
    ranks = {}
    for node in inlink_map.keys(): ranks[node] = initial_value
    
    new_ranks = {}
    delta = 1.0
    n_iterations = 0
    while delta > epsilon:
        new_ranks = {}
        for node, inlinks in inlink_map.items():
            new_ranks[node] = ((1 - damping) / len(all_nodes)) + (damping * sum(ranks[inlink] / outlink_counts[inlink] for inlink in inlinks))
        delta = sum(abs(new_ranks[node] - ranks[node]) for node in new_ranks.keys())
        ranks, new_ranks = new_ranks, ranks
        n_iterations += 1
    
    return ranks, n_iterations
'''
        