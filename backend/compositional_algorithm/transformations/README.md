# Transformations

A transformation is a tuple `ρ = (L, R,cL,cR)` where:

1. `L` is the left part – a subnet to be transformed. 
2. `R` is the right part – a subnet that replaces L. 
3. `cL` – constraints imposed on L.
4. `cR` – constraints imposed on R.

One can implement Transformations as functions or classes. We decide to use `functions` for the following reasons:

- P1,....,P4 Transformations are simple and stateless.
- No need to maintain or track state across multiple transformations.
- The implementation stays minimal and straightforward.