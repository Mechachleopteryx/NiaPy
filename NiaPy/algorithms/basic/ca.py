# encoding=utf8
import numpy as np
from NiaPy.algorithms.algorithm import Algorithm
from NiaPy.benchmarks.utility import Task

__all__ = ['CamelAlgorithm']

class Camel(object):
	r"""Implementation of population individual that is a camel for Camel algorithm.
	**Algorithm:** Camel algorithm
	**Date:** 2018
	**Authors:** Klemen Berkovič
	**License:** MIT
	"""
	E_init, S_init = 1, 1
	T_min, T_max = -1, 1

	def __init__(self, x, rand):
		self.E, self.E_past = Camel.E_init, Camel.E_init
		self.S, self.S_past = Camel.S_init, Camel.S_init
		self.x, self.x_past = x, x
		self.rand = rand
		self.steps = 0

	def nextT(self): self.T = (Camel.T_max - Camel.T_min) * self.rand() + Camel.T_min

	def nextS(self, omega, n_gens): self.S = self.S_past * (1 - omega * self.steps / n_gens)

	def nextE(self, n_gens): self.E = self.E_past * (1 - self.T / Camel.T_max) * (1 - self.steps / n_gens)

	def nextX(self, x_best, task):
		delta = -1 + self.rand() * 2
		self.x = self.x_past + delta * (1 - (self.E / Camel.E_init)) * np.exp(1 - self.S / Camel.S_init) * (x_best - self.x_past)
		if not task.isFisible(self.x):
			self.x = self.x_past
			return False
		else: 
			return True

	def next(self):
		self.x_past, self.E_past, self.S_past = self.x, self.E, self.S
		self.steps += 1

	def refill(self, S = None, E = None):
		self.S = Camel.S_init if S == None else S
		self.E = Camel.E_init if E == None else E
	
	def __getitem__(self, i): return self.x[i]

class CamelAlgorithm(Algorithm):
	r"""Implementation of Camel traveling behavior.
	**Algorithm:** Camel algorithm
	**Date:** 2018
	**Authors:** Klemen Berkovič
	**License:** MIT
	**Reference URL:**
		https://www.iasj.net/iasj?func=fulltext&aId=118375
	**Reference paper:**
		Ali, Ramzy. (2016). Novel Optimization Algorithm Inspired by Camel Traveling Behavior. Iraq J. Electrical and Electronic Engineering. 12. 167-177.
	"""
	def __init__(self, NP, D, nGEN, nFES, omega, mu, alpha, S_init, E_init, T_min, T_max, benchmark):
		r"""**__init__(self, NP, D, nFES, T_min, T_max, omega, S_init, E_init, benchmark)**.
		Arguments:
		NP {integer} -- population size
		D {integer} -- dimension of problem
		nGEN {integer} -- nuber of generation/iterations
		nFES {integer} -- number of function evaluations
		T_min {real} -- minimum temperature
		T_max {real} -- maximum temperature
		omega {real} -- (0, 1] -- burden factor
		mu {real} -- [0, 1) -- dying rate
		S_init {real} -- (0, inf) -- initial supply
		E_init {real} -- (0, inf) -- initial endurance
		benchmark {object} -- benchmark implementation object
		"""
		super().__init__('CamelAlgorithm', 'CA')
		self.NP, self.omega, self.mu, self.alpha, self.S_init, self.E_init, self.T_min, self.T_max = NP, omega, mu, alpha, S_init, E_init, T_min, T_max
		self.task = Task(D, nFES, nGEN, benchmark)

	def __init__(self, **kwargs):
		# TODO
		pass

	def __init__(self, taks, **kwargs):
		# TODO
		pass

	def setParameters(self, **kwargs):
		# TODO
		pass

	def walk(self, c, fit, task, omega, c_best):
		c.nextT()
		c.nextS(omega, task.nGEN)
		c.nextE(task.nGEN)
		if c.nextX(c_best.x, task):
			c.next()
			return c, task.eval(c.x)
		else: 
			return c, fit

	def oasis(self, c, rn, fit, fitn, alpha): 
		if rn > 1 - alpha and fit < fitn: c.refill(Camel.S_init, Camel.E_init)
		return c

	def lifeCycle(self, c, fit, fitn, mu, task):
		if fit < mu * fitn:
			cn = Camel(c.rand(task.D) * task.bRange, c.rand)
			return cn, task.eval(cn.x)
		else:
			return c, fitn

	def runTask(self, task):
		Camel.E_init, Camel.S_init, rand = self.E_init, self.S_init, np.random.RandomState().rand
		ccaravan = [Camel(np.random.uniform(task.Lower, task.Upper, [task.D]), rand) for i in range(self.NP)]
		c_fits = [task.eval(c.x) for c in ccaravan]
		ic_b = np.argmin(c_fits)
		c_best, c_best_fit = ccaravan[ic_b], c_fits[ic_b]
		while not task.stopCond():
			ccaravan, c_fitsn = np.vectorize(self.walk)(ccaravan, c_fits, task, self.omega, c_best)
			ccaravan = np.vectorize(self.oasis)(ccaravan, np.random.randn(self.NP), c_fits, c_fitsn, self.alpha)
			ci_b = np.argmin(c_fitsn)
			if c_fits[ci_b] < c_best_fit: c_best, c_best_fit = ccaravan[ci_b], c_fits[ci_b]
			ccaravan, c_fitsn = np.vectorize(self.lifeCycle)(ccaravan, c_fits, c_fitsn, self.mu, task)
			c_fits = c_fitsn
			task.nextIter()
		return c_best.x, c_best_fit

	def run(self): return self.runTask(self.task)

# vim: tabstop=3 noexpandtab shiftwidth=3 softtabstop=3
