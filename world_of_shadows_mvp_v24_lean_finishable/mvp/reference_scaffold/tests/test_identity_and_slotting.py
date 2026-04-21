from wos_mvp.identity import EntityIdentityResolver
from wos_mvp.slotting import AssertionSlotResolver

def test_alias_resolution() -> None:
    resolver = EntityIdentityResolver({"Vera Chen": "vera_chen", "vera": "vera_chen"})
    assert resolver.canonicalize("Vera Chen") == "vera_chen"
    assert resolver.same_entity("vera", "Vera Chen")

def test_slot_key_is_canonicalized() -> None:
    identity = EntityIdentityResolver({"Vera Chen": "vera_chen"})
    slots = AssertionSlotResolver(identity)
    key = slots.make_slot_key("Vera Chen", "canonical", "money_trail", "scene_1", "session")
    assert key.startswith("vera_chen::canonical::money_trail::scene_1::session")
