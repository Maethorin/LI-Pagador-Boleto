#!/bin/sh

test:
	@echo "Iniciando os testes"
	coverage2 run `which nosetests` tests/unitarios tests/integracao
	coverage2 report -m --fail-under=70