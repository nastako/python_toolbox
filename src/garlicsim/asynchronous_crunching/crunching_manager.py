# Copyright 2009 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

"""
This module defines the CrunchingManager class. See its documentation for more
information.
"""

import garlicsim
from garlicsim.misc.nodes_added import NodesAdded
from crunchers import CruncherThread, CruncherProcess
from crunching_profile import CrunchingProfile


import garlicsim.general_misc.dict_tools #todo: example of inconsistent import policy
import garlicsim.general_misc.queue_tools as queue_tools
import garlicsim.general_misc.third_party.decorator
from garlicsim.general_misc.infinity import Infinity


PreferredCruncher = [CruncherThread, CruncherProcess][0]
# Should make a nicer way of setting that.

__all__ = ["CrunchingManager"]

@garlicsim.general_misc.third_party.decorator.decorator
def with_tree_lock(method, *args, **kwargs):
    """
    A decorator used in CrunchingManager's methods to use the tree lock (in
    write mode) as a context manager when calling the method.
    """
    self = args[0]
    with self.project.tree_lock.write:
        return method(*args, **kwargs)


class CrunchingManager(object):
    """
    A crunching manager manages the background crunching for a project.
    
    Every project creates a crunching manager. The job of the crunching manager
    is to coordinate the crunchers, creating and retiring them as necessary.
    The main use of a crunching manager is through its sync_workers methods,
    which goes over all the crunchers and all the nodes of the tree that need
    to be crunched, making sure the crunchers are working on these nodes, and
    collecting work from them to implement into the tree.
    """
    def __init__(self, project):        
        self.project = project
        
        if project.simpack_grokker.history_dependent:
            self.Cruncher = CruncherThread
        else:
            self.Cruncher = PreferredCruncher
        
        self.jobs = []
        '''tododoc'''
        
        self.crunchers = {}
        """tododoc, should map JOBS to crunchers.
        A dict that maps nodes that should be worked on to crunchers.
        """
        
        self.crunhing_profile
        
        todo, use hash to see when crunhing profile changed
        
    @with_tree_lock
    def sync_crunchers(self):
        """
        Take work from the crunchers, and give them new instructions if needed.
        
        Talks with all the crunchers, takes work from them for implementing
        into the tree, retiring crunchers or recruiting new crunchers as
        necessary.

        Returns the total amount of nodes that were added to the tree in the
        process.
        """
        tree = self.project.tree
        
        total_added_nodes = NodesAdded(0)

        for (job, cruncher) in self.crunchers.copy().items():
            if not (job in self.jobs):
                (added_nodes, new_leaf) = \
                    self.__add_work_to_tree(cruncher, node, retire=True)
                total_added_nodes += added_nodes
                del self.crunchers[job]


        for job in self.jobs.copy():
            
            job_done = job.is_done()
            
            if self.crunchers.has_key(job) is False:
                if not job_done:
                    self.__conditional_create_cruncher(job)
                else: # job_done is True
                    self.jobs.remove(job)
                continue

            # self.crunchers.has_key(job) is True
            
            cruncher = self.crunchers[job]
            
            (added_nodes, new_leaf) = self.__add_work_to_tree(cruncher, node)
            total_added_nodes += added_nodes

            job.node = new_leaf
            
            if not job_done:
                if cruncher.is_alive():
                    if CRUNCHING PROFILE CHANGED TODO:
                        cruncher.update_crunching_profile(crunching_profile)
                else:
                    self.__conditional_create_cruncher(new_leaf, crunching_profile)
            else: # job_done is True           
                self.jobs.remove(job)
                if cruncher.is_alive():
                    cruncher.retire()
                del self.crunchers[job]
            
        return total_added_nodes

    
    def __conditional_create_cruncher(self, job):
        '''
        Create a cruncher to crunch the node, unless there is reason not to.
        '''
        if node.still_in_editing is False:
            step_function = self.project.simpack_grokker.step
            if self.Cruncher == CruncherProcess:
                cruncher = self.Cruncher \
                         (node.state,
                          self.project.simpack_grokker.step_generator,
                          crunching_profile=crunching_profile)
            else: # self.Cruncher == CruncherThread
                cruncher = self.Cruncher(node.state, self.project,
                                         crunching_profile=crunching_profile)
            cruncher.start()
            self.crunchers[node] = cruncher
            return cruncher
    
    def get_jobs_by_node(self, node):
        return [job for jobs in self.jobs if job.node == node]
    
    def __add_work_to_tree(self, cruncher, node, retire=False): #todo: modify this to take job?
        """
        Take work from the cruncher and add to the tree at the specified node.
        
        If `retire` is set to True, retires the cruncher.
        
        Returns (number, leaf), where `number` is the number of nodes that
        were added, and `leaf` is the last node that was added.
        """
        tree = self.project.tree
        states = queue_tools.dump(cruncher.work_queue)
        if retire:
            cruncher.retire()
        current = node
        for state in states:
            current = tree.add_state(state, parent=current)
        nodes_added = NodesAdded(len(states))
        return (nodes_added, current)
    
    
    
    
    
    