# Negative Path Contract

COLLIDER must demonstrate a case it cannot safely resolve.

Required sequence:
1. parallel agents disagree
2. source lookup finds no decisive evidence
3. classifier returns SPEC_GAP
4. epistemic state remains UNKNOWN
5. implementation that depends on the missing decision does not silently canonize one interpretation
6. system asks one minimal human question
7. unrelated work may continue if dependency analysis shows it is unaffected

Success criterion:
Correct abstention is treated as product success, not a demo failure.