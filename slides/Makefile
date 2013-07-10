all: html pdf
	
html: psycopg.html

pdf: psycopg.pdf

psycopg.html: psycopg.rst
	landslide psycopg.cfg

psycopg.pdf: psycopg.rst
	landslide psycopg-pdf.cfg
