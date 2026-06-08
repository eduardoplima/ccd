"""Admin-only dataset correction surface.

Lets admins review the cleanlab-flagged token errors in
``dataset/errors/erros_anotacao_decicontas.csv``, decide accept/reject/custom
for each, and export a JSON of corrections that a downstream script applies
to the CONLL.
"""
