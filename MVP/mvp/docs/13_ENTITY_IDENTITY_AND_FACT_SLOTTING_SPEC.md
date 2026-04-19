# 13 — Entity Identity and Fact Slotting Specification

Each assertion must resolve to:
- canonical entity id
- assertion scope
- field name
- temporal bucket
- partition scope

Two records may only compete for supersession or contradiction handling if they refer to the same world, module, entity, assertion scope, fact field, and temporal bucket.
