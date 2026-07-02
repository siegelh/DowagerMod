# DowagerMod — New Leader/Civ Suggestion Prompt

You are designing new **leaders and civilizations** for DowagerMod (a Civilization IV:
Beyond the Sword overhaul) that **reuse currently-unused leaderhead art** already present in
the repo.

## The pattern (required)

For each proposal, follow the mod's established 1:1 pattern:

- **One NEW leader** paired with **exactly one civilization**.
- The leader gets **exactly one bespoke custom trait** (`TRAIT_*`) that does **not** already
  exist — it is designed specifically for this leader (mirroring existing custom traits like
  `TRAIT_STALIN`, `TRAIT_ROOSEVELT`, `TRAIT_VICTORIA`).
- The leader + civilization + custom trait are designed **together** as a coherent unit.

## Hard rules

- Each proposal: exactly one NEW custom_trait (TRAIT_* that does NOT already exist) unique to that leader.
- leader_type and (if new_civilization) civilization_type must not collide with any existing id below.
- favorite_civic must be one of available_civics; art_style (for a new civ) must be one of available_art_styles.
- leaderhead.nif and leaderhead.kfm MUST be copied verbatim from a candidate below (they are verified-unused, on-disk art).
- Only add a unique_unit / unique_building if you can point it at an unused art path from candidate_units / candidate_buildings.
- Prefer historically coherent leader+civ+trait triples that fit the mod's era/dynasty-specific civ style.

## Live game context

Existing civilizations (61), leaders (60), traits (71). Available civics: CIVIC_BARBARISM, CIVIC_BUREAUCRACY, CIVIC_CASTE_SYSTEM, CIVIC_DECENTRALIZATION, CIVIC_DESPOTISM, CIVIC_EMANCIPATION, CIVIC_ENVIRONMENTALISM, CIVIC_FREE_MARKET, CIVIC_FREE_RELIGION, CIVIC_FREE_SPEECH, CIVIC_HEREDITARY_RULE, CIVIC_MERCANTILISM, CIVIC_NATIONHOOD, CIVIC_ORGANIZED_RELIGION, CIVIC_PACIFISM, CIVIC_PAGANISM, CIVIC_POLICE_STATE, CIVIC_REPRESENTATION, CIVIC_SERFDOM, CIVIC_SLAVERY, CIVIC_STATE_PROPERTY, CIVIC_THEOCRACY, CIVIC_TRIBALISM, CIVIC_UNIVERSAL_SUFFRAGE, CIVIC_VASSALAGE. Art styles: ARTSTYLE_ASIAN, ARTSTYLE_BARBARIAN, ARTSTYLE_EUROPEAN, ARTSTYLE_GRECO_ROMAN, ARTSTYLE_MIDDLE_EAST, ARTSTYLE_SOUTH_AMERICA.

## Output

Return JSON conforming to `tools/leader_suggest/suggestion_spec.schema.json`:
a top-level object with a `proposals` array. Copy `leaderhead.nif` / `leaderhead.kfm`
**verbatim** from the candidate table so the art wiring is guaranteed valid. Then run:

```
python tools/leader_suggest/suggest_leaders.py validate <your_proposals.json>
```

## Unused leaderhead candidates

Each row is a verified-unused, on-disk leaderhead you may reuse. `nif`/`kfm` are the
Assets-relative model paths to copy into `leaderhead`.

| leader_label | tier | pair | hints | nif | kfm |
| --- | --- | --- | --- | --- | --- |
| Ruga | BTG | high | ancient,asian,middle_eastern | Art/BTG/Huns/leaderheads/Ruga/genghis_khan.nif | Art/BTG/Huns/leaderheads/Ruga/genghis_khan.kfm |
| Franz Joseph | BTG | high | colonial,european | Art/BTG/LeaderHeads/Franz Joseph/napoleon.nif | Art/BTG/LeaderHeads/Franz Joseph/napoleon.kfm |
| Hirohito | base-game | high | colonial,european | Art/Leaderheads/new/Emperor Hirohito 0.1/LeaderHeads/Hirohito/napoleon.nif | Art/Leaderheads/new/Emperor Hirohito 0.1/LeaderHeads/Hirohito/napoleon.kfm |
| George I | base-game | high | colonial,european | Art/Leaderheads/new/George I/Assets/Modules/Custom LeaderHeads/George I/fdr.nif | Art/Leaderheads/new/George I/Assets/Modules/Custom LeaderHeads/George I/fdr.kfm |
| Alexander the  Great | base-game | high | ancient,asian,middle_eastern | Art/Leaderheads/new/alexander_take_this_firaxis/art/leaderheads/Alexander_the _Great/alexander.nif | Art/Leaderheads/new/alexander_take_this_firaxis/art/leaderheads/Alexander_the _Great/alexander.kfm |
| christian | base-game | high | colonial,european | Art/Leaderheads/new/christian/peter.nif | Art/Leaderheads/new/christian/peter.kfm |
| dompedro v3 | base-game | high | colonial,european | Art/Leaderheads/new/dompedro_v3/napoleon.nif | Art/Leaderheads/new/dompedro_v3/napoleon.kfm |
| dufour | base-game | high | colonial,european | Art/Leaderheads/new/dufour/John_Adams.nif | Art/Leaderheads/new/dufour/John_Adams.kfm |
| freydis | base-game | high | medieval,european | Art/Leaderheads/new/freydis/victoria.nif | Art/Leaderheads/new/freydis/victoria.kfm |
| Harold | base-game | high | medieval,european | Art/Leaderheads/new/harold/Harold/ragnar_lodbrok.nif | Art/Leaderheads/new/harold/Harold/ragnar_lodbrok.kfm |
| john hunyadi | base-game | high | medieval,european | Art/Leaderheads/new/john_hunyadi/alexander.nif | Art/Leaderheads/new/john_hunyadi/alexander.kfm |
| kanishka | base-game | high | medieval,european | Art/Leaderheads/new/kanishka/ragnar_lodbrok.nif | Art/Leaderheads/new/kanishka/ragnar_lodbrok.kfm |
| lmm | base-game | high | colonial,european | Art/Leaderheads/new/lmm/charles de gaulle.nif | Art/Leaderheads/new/lmm/Charles De Gaulle.kfm |
| louis xvi | base-game | high | colonial,european | Art/Leaderheads/new/louis_xvi/King_English.nif | Art/Leaderheads/new/louis_xvi/King_English.kfm |
| macha mong ruad | base-game | high | ancient,european | Art/Leaderheads/new/macha_mong_ruad/Macha Mong Ruad.nif | Art/Leaderheads/new/macha_mong_ruad/Macha Mong Ruad.kfm |
| mongkut | base-game | high | colonial,european | Art/Leaderheads/new/mongkut/Tachnechobrus.nif | Art/Leaderheads/new/mongkut/Tachnechobrus.kfm |
| pyrrhusfinal | base-game | high | medieval,european | Art/Leaderheads/new/pyrrhusfinal/alexander.nif | Art/Leaderheads/new/pyrrhusfinal/alexander.kfm |
| rahman | base-game | high | colonial,european | Art/Leaderheads/new/rahman/Zara Yaqob.nif | Art/Leaderheads/new/rahman/Zara Yaqob.kfm |
| robert bruce gabihime | base-game | high | colonial,european | Art/Leaderheads/new/robert_bruce_gabihime/napoleon.nif | Art/Leaderheads/new/robert_bruce_gabihime/napoleon.kfm |
| ruga | base-game | high | ancient,asian,middle_eastern | Art/Leaderheads/new/ruga/genghis_khan.nif | Art/Leaderheads/new/ruga/genghis_khan.kfm |
| seleucus | base-game | high | ancient,european | Art/Leaderheads/new/seleucus/hannibal.nif | Art/Leaderheads/new/seleucus/hannibal.kfm |
| suppiluliuma  hittite    amra | base-game | high | ancient,asian | Art/Leaderheads/new/suppiluliuma__hittite____amra/kublai_khan.nif | Art/Leaderheads/new/suppiluliuma__hittite____amra/kublai_khan.kfm |
| szechenyi | base-game | high | colonial,european | Art/Leaderheads/new/szechenyi/Szechenyi.nif | Art/Leaderheads/new/szechenyi/Szechenyi.kfm |
| Trader | base-game | high | ancient,asian | Art/Leaderheads/new/venice_v3/Assets/Modules/Custom Civilizations/Venice/Trader/greatmerchantancient.nif | Art/Leaderheads/new/venice_v3/Assets/Modules/Custom Civilizations/Venice/Trader/greatmerchantancient.kfm |
| william | base-game | high | medieval,european | Art/Leaderheads/new/william/Charlemagne.nif | Art/Leaderheads/new/william/Charlemagne.kfm |
| austin2 | base-game | low | colonial,european | Art/Leaderheads/new/austin2/austin.nif | Art/Leaderheads/new/austin2/Samuel_de_Champlain.kfm |
| cardenas | base-game | low | colonial,european | Art/Leaderheads/new/cardenas/NewEarth.nif | Art/Leaderheads/new/cardenas/napoleon.kfm |
| francisco franco v2 | base-game | low | colonial,european | Art/Leaderheads/new/francisco_franco_v2/Francisco_Franco_V2_Cap.nif | Art/Leaderheads/new/francisco_franco_v2/josef_stalin.kfm |
| giovanni messe | base-game | low | colonial,european | Art/Leaderheads/new/giovanni_messe/Messe.nif | Art/Leaderheads/new/giovanni_messe/josef_stalin.kfm |
| gunnhild | base-game | low | ancient,asian,middle_eastern | Art/Leaderheads/new/gunnhild/Gunnhild.nif | Art/Leaderheads/new/gunnhild/alexander_BG.kfm |
| hselassie | base-game | low | colonial,european | Art/Leaderheads/new/hselassie/Hselassie.nif | Art/Leaderheads/new/hselassie/saladin.kfm |
| napoleoniii | base-game | low | colonial,european | Art/Leaderheads/new/napoleoniii/napoleonIII.nif | Art/Leaderheads/new/napoleoniii/cyrus.kfm |
| Antiochus | base-game | low | ancient,european | Art/Leaderheads/new/newgreeks/Antiochus/AlexWCrown.nif | Art/Leaderheads/new/newgreeks/Antiochus/alexander.kfm |
| Pyrrhus | base-game | low | ancient,medieval,european | Art/Leaderheads/new/newgreeks/Pyrrhus/AlexWHelm.nif | Art/Leaderheads/new/newgreeks/Pyrrhus/alexander.kfm |
| o higgins | base-game | low | colonial,european | Art/Leaderheads/new/o_higgins/OHiggins.nif | Art/Leaderheads/new/o_higgins/augustus_caesar.kfm |
| European Saminfantry | base-game | low | modern,european | Art/Leaderheads/new/venice_v3/Assets/Modules/Varietas Delectat/Art/Units/Europe/European Saminfantry/saminfantry.nif | - |
| European War Elephant | base-game | low | ancient,european | Art/Leaderheads/new/venice_v3/Assets/Modules/Varietas Delectat/Art/Units/Europe/European War Elephant/warelephant_fx.nif | - |
| celtic worker | base-game | low | ancient,european | Art/Leaderheads/new/venice_v3/Assets/Modules/Varietas Delectat/Art/Units/Europe/celtic worker/worker_celtic.nif | - |
| Holy Roman Musketman | base-game | low | ancient,colonial,medieval,european | Art/Leaderheads/new/venice_v3/Assets/Modules/Varietas Delectat/Art/Units/holy rome/Holy Roman Musketman/musketman.nif | - |
| Italy Cavalry | base-game | low | industrial,european | Art/Leaderheads/new/venice_v3/Assets/Modules/Varietas Delectat/Art/Units/italy/Italy Cavalry/italiancavalry.nif | - |
