from sqlalchemy import func
from initDB import Paper, Conference, PCMembership, SubmissionsCount


class ConferenceMetrics():
    def __init__(self, session, conference):
        self.session = session
        self.name = conference
        
        """Helper data structures"""
        self.authorsPerYear = self.__extractAuthors();  """Look up the authors that published in a particular year"""
        self.papersPerYear = self.__extractPapers();    """Look up the papers (paper = list of authors) published in a particular year"""
        self.pcPerYear = self.__extractPC();            """Look up the PC members for a particular year"""
        
        """Metrics"""
        self.AP = self.__computeAP();   """Number of accepted papers per year"""
        self.SP = self.__computeSP();   """Number of submissions per year"""
        self.RA = self.__computeRA();   """Acceptance rate: #acc/#subm"""
        self.RL = self.__computeRL();   """Review load: #subm/#PCmem"""
        self.A = self.__computeA();     """Number of authors per year"""
        self.C = self.__computeC();     """Number of PC members per year"""
        
        self.CnA4 = self.__computeCnA(4);   """Number of PC members for a given year that have never been authors between y-n and y-1"""
        self.RCnA4 = self.__computeRCnA(4); """Wild-Card Ratio: %PC members for a given year that have never been authors between y-n and y-1 (sliding window)"""
        
        self.APC0 = self.__computeAPC(0);   """Number of papers published in a given year that have at least one PC member from y-n..y as author"""
        
        self.RAC0 = self.__computeRAC(0);   """Inbreeding ratio (IR): fraction of papers published in a given year that have at least one PC member from y-n..y as author"""
        self.RAC4 = self.__computeRAC(4)
        
        self.NC1 = self.__computeNC(1);     """PC Turnover: number of PC members for a given year that have not been on the PC between y-n and y-1"""
        self.NC4 = self.__computeNC(4)
        self.RNC1 = self.__computeRNC(1);   """PC Turnover Ratio: fraction of PC members for a given year that have not been on the PC between y-n and y-1"""
        self.RNC4 = self.__computeRNC(4)
        
        self.NA1 = self.__computeNA(1);     """Author Turnover: number of authors for a given year that have not been author between y-n and y-1"""
        self.NA4 = self.__computeNA(4);
        self.RNA1 = self.__computeRNA(1);   """Author Turnover Ratio: fraction of authors for a given year that have not been author between y-n and y-1"""
        self.RNA4 = self.__computeRNA(4);
        
        self.PNA4 = self.__computePNA(4);   """Number of papers published in a given year for which none of the co-authors has published here between y-n and y-1"""
        self.RPNA4 = self.__computeRPNA(4); """Fraction of the papers published in a given year for which none of the co-authors has published here between y-n and y-1"""

            
    def getMetric(self, metric, k=None):
        if metric == 'AP':
            return self.AP
        
        elif metric == 'SP':
            return self.SP
        
        elif metric == 'RA':
            return self.RA
        
        elif metric == 'RL':
            return self.RL
        
        elif metric == 'A':
            return self.A
        
        elif metric == 'C':
            return self.C
        
        elif metric == 'CnA':
            if k is not None and k == 4:
                return self.CnA4
            else:
                return self.__computeCnA(k)
        
        elif metric == 'RCnA':
            if k is not None:
                if k == 4:
                    return self.RCnA4
                else:
                    return self.__computeRCnA(k)
        
        elif metric == 'APC':
            if k is not None:
                if k == 0:
                    return self.APC0
                else:
                    return self.__computeAPC(k)
            
        elif metric == 'RAC':
            if k is not None:
                if k == 0:
                    return self.RAC0
                elif k == 4:
                    return self.RAC4
                else:
                    return self.__computeRAC(k)
                
        elif metric == 'NC':
            if k is not None:
                if k == 1:
                    return self.NC1
                elif k == 4:
                    return self.NC4
                else:
                    return self.__computeNC(k)
            
        elif metric == 'RNC':
            if k is not None:
                if k == 1:
                    return self.RNC1
                elif k == 4:
                    return self.RNC4
                else:
                    return self.__computeRNC(k)
            
        elif metric == 'NA':
            if k is not None:
                if k == 1:
                    return self.NA1
                elif k == 4:
                    return self.NA4
                else:
                    return self.__computeNA(k)
            
        elif metric == 'RNA':
            if k is not None:
                if k == 1:
                    return self.RNA1
                elif k == 4:
                    return self.RNA4
                else:
                    return self.__computeRNA(k)
                
        elif metric == 'PNA':
            if k is not None:
                if k == 4:
                    return self.PNA4
                else:
                    return self.__computePNA(k)
            
        elif metric == 'RPNA':
            if k is not None:
                if k == 4:
                    return self.RPNA4
                else:
                    return self.__computeRPNA(k)

            
    def __extractAuthors(self):
        """Look up the authors that published in a particular year"""
        d = {}
        for paper in self.session.query(Paper).\
                            join(Conference).\
                            filter(Conference.acronym == self.name).\
                            filter(Paper.main_track == True):
            year = paper.year
            if year not in d.keys():
                d[year] = set()
            for author in paper.authors:
                d[year].add(author.name)
        return d
            
    
    def __extractPapers(self):
        """Look up the papers (paper = list of authors) published in a particular year"""
        d = {}
        for paper in self.session.query(Paper).\
                            join(Conference).\
                            filter(Conference.acronym == self.name).\
                            filter(Paper.main_track == True):
            year = paper.year
            if year not in d.keys():
                d[year] = []
            d[year].append(set([author.name for author in paper.authors]))
        return d
    
          
    def __computeA(self):
        """Number of authors per year"""
        a = self.authorsPerYear
        d = {}
        for year in a.keys():
            d[year] = len(a[year])
        return d
    
            
    def __extractPC(self):
        """Look up the PC members for a particular year"""
        d = {}
        for pcm in self.session.query(PCMembership).\
                            join(Conference).\
                            filter(Conference.acronym == self.name):
            year = pcm.year
            if year not in d.keys():
                d[year] = set()
            d[year].add(pcm.pcmember.name)
        return d


    def __computeC(self):
        """Number of PC members per year"""
        d = {}
        pc = self.pcPerYear
        for year in pc.keys():
            d[year] = len(pc[year])
        return d


    def __computeSP(self):
        '''Compute the number of submissions per conference per year'''
        d = {}
        for y, n in self.session.query(SubmissionsCount.year, SubmissionsCount.number).\
                            filter(SubmissionsCount.conference_id == Conference.id).\
                            filter(Conference.acronym == self.name).\
                            all():
            d[y] = n
        return d


    def __computeAP(self):
        d = {}
        '''Compute the number of accepted papers per conference per year'''
        for y, n in self.session.query(Paper.year, func.count(Paper.id)).\
                                filter(Paper.conference_id == Conference.id).\
                                filter(Paper.main_track == True).\
                                filter(Conference.acronym == self.name).\
                                group_by(Paper.year).\
                                all():
            d[y] = n
        return d


    def __computeRA(self):
        """Acceptance rate: #acc/#subm"""
        d = {}
        sp = self.SP
        ap = self.AP
        for year in set(sp.keys()).intersection(set(ap.keys())):
            d[year] = float(ap[year]) / float(sp[year])
        return d


    def __computeRL(self):
        """Reviewer load: #subm/#PCmem"""
        d = {}
        c = self.pcPerYear
        sp = self.SP
        for year in set(sp.keys()).intersection(set(c.keys())):
            d[year] = float(sp[year]) / float(len(c[year]))
        return d        


    def __absWindow(self, data, k):
        d = {}
        years = sorted(data.keys())
        for year in years[k:]:
            previous = set()
            for y in [y for y in years[years.index(year)-k: years.index(year)]]:
                previous.update(data[y])
            d[year] = len(data[year].difference(previous))
        return d

    
    def __ratioWindow(self, data, k):
        d = {}
        years = sorted(data.keys())
        for year in years[k:]:
            previous = set()
            for y in [y for y in years[years.index(year)-k: years.index(year)]]:
                previous.update(data[y])
            d[year] = float(len(data[year].difference(previous))) / float(len(data[year]))
        return d


    def __computeAPC(self, k=0):
        """Number of papers published in a given year that have at least one PC member from y-n..y as author"""
        papers = self.papersPerYear
        pc = self.pcPerYear
        pcAuthored = {}
        years = sorted(set(pc.keys()).intersection(papers.keys()))
        for year in years[k:]:
            pcAuthored[year] = 0
            previous = set()
            for y in [y for y in years[years.index(year)-k: years.index(year)+1]]:
                previous.update(pc[y])
            for paper in papers[year]:
                if len(paper.intersection(previous)):
                    pcAuthored[year] += 1
        return pcAuthored


    def __computeRAC(self, k):
        """Inbreeding ratio (IR): fraction of papers published in a given year that have at least one PC member from y-n..y as author"""
        pcAuthored = self.__computeAPC(k)
        papers = self.papersPerYear
        d = {}
        for year in pcAuthored.keys():
            d[year] = float(pcAuthored[year]) / float(len(papers[year]))
        return d
          
          
    def __computeCnA(self, k=4):
        """Number of PC members for a given year that have never been authors between y-n and y-1"""
        authors = self.authorsPerYear
        pc = self.pcPerYear
        d = {}
        years = sorted(set(pc.keys()).intersection(authors.keys()))
        for year in years[k:]:
            d[year] = 0
            previous = set()
            for y in [y for y in years[years.index(year)-k: years.index(year)]]:
                previous.update(authors[y])
            d[year] = len(pc[year].difference(previous))
        return d
    
    
    def __computeRCnA(self, k=4):
        """Wild-Card Ratio: %PC members for a given year that have never been authors between y-n and y-1"""
        pc = self.pcPerYear
        count = self.__computeCnA(k)
        d = {}
        for year in count.keys():
            d[year] = float(count[year]) / float(len(pc[year]))
        return d
        
            
    def __computeNA(self, k):
        """Author Turnover: number of authors for a given year that have not been author between y-n and y-1"""
        return self.__absWindow(self.authorsPerYear, k)


    def __computeRNA(self, k):
        """Author Turnover Ratio: fraction of authors for a given year that have not been author between y-n and y-1"""
        return self.__ratioWindow(self.authorsPerYear, k)


    def __computeNC(self, k):
        """PC Turnover: number of PC members for a given year that have not been on the PC between y-n and y-1"""
        return self.__absWindow(self.pcPerYear, k)


    def __computeRNC(self, k):
        """PC Turnover Ratio: fraction of PC members for a given year that have not been on the PC between y-n and y-1"""
        return self.__ratioWindow(self.pcPerYear, k)


    def __computePNA(self, k):
        """Number of papers published in a given year for which none of the co-authors has published here between y-n and y-1"""
        papers = self.papersPerYear
        authors = self.authorsPerYear
        d = {}
        years = sorted(set(authors.keys()).intersection(papers.keys()))
        for year in years[k:]:
            d[year] = 0
            previous = set()
            for y in [y for y in years[years.index(year)-k: years.index(year)]]:
                previous.update(authors[y])
            for paper in papers[year]:
                if len(paper.intersection(previous)) == 0:
                    d[year] += 1
        return d
    
    
    def __computeRPNA(self, k):
        """Fraction of the papers published in a given year for which none of the co-authors has published here between y-n and y-1"""
        papers = self.papersPerYear
        before = self.__computePNA(k)
        d = {}
        for year in before.keys():
            d[year] = float(before[year])/ float(len(papers[year]))
        return d

    
