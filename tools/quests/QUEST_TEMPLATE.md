# Quest Authoring Template

This is the canonical reference for adding a new BtS random-event quest to DowagerMod.

Modelled on the vanilla **Greed** (single reward) and **Horse Whispering** (3-choice reward) quests.

## Files to touch (per quest)

| File | What you add |
|------|---------------|
| `CIV4EventTriggerInfos.xml` | 1 start trigger + 1 done trigger |
| `CIV4EventInfos.xml` | 1 start event + 1–3 done events (one per reward choice) |
| `CIV4GameText_Events_BTS.xml` | 8–14 `TXT_KEY_*` entries |
| `CvRandomEventInterface.py` | Optional `canTrigger*` / `applyEvent*Done*` / `getHelp*` (Tier 2 only) |

## Required text keys per quest (with N reward choices)

```
TXT_KEY_EVENT_TRIGGER_<NAME>_1            # start popup body
TXT_KEY_EVENTTRIGGER_<NAME>_DONE          # WorldNews announcement when quest completes
TXT_KEY_EVENT_TRIGGER_<NAME>_DONE_1       # done popup body
TXT_KEY_EVENT_<NAME>_1                    # start event description (button + quest log title)
TXT_KEY_EVENT_<NAME>_QUEST                # quest log objective text
TXT_KEY_EVENT_FAIL_<NAME>                 # quest-failure text (if expirable)
TXT_KEY_EVENT_<NAME>_DONE_1               # reward choice 1 label
TXT_KEY_EVENT_<NAME>_DONE_1_HELP          # reward choice 1 help tooltip
... (repeat _DONE_N + _DONE_N_HELP for each additional choice)
```

## Naming conventions

- Trigger ID: `EVENTTRIGGER_<UPPER_SNAKE_NAME>` + `_DONE`
- Event ID: `EVENT_<UPPER_SNAKE_NAME>_1` (start), `EVENT_<UPPER_SNAKE_NAME>_DONE_<N>` (each choice)
- Python callbacks: `canTrigger<CamelName>`, `expire<CamelName>1`, `applyEvent<CamelName>Done<N>`, `getHelp<CamelName><N>`

## Reference: Greed (single reward)

See:
- Trigger: `CIV4EventTriggerInfos.xml` line ~13937 (`EVENTTRIGGER_GREED`)
- Done trigger: same file ~14017 (`EVENTTRIGGER_GREED_DONE`)
- Start event: `CIV4EventInfos.xml` ~21580 (`EVENT_GREED_1`)
- Done event: same file ~21661 (`EVENT_GREED_DONE_1`)
- Python: `CvRandomEventInterface.py` — search `canTriggerGreed`, `expireGreed1`, `applyGreedDone1`, `getHelpGreed1`

## Reference: Horse Whispering (3 reward choices)

See:
- Trigger: `CIV4EventTriggerInfos.xml` (search `EVENTTRIGGER_HORSE_WHISPERING`)
- Start event: `CIV4EventInfos.xml` (`EVENT_HORSE_WHISPERING_1`)
- Done events: 3 entries `EVENT_HORSE_WHISPERING_DONE_1/2/3`
- Each done event's `<PrereqEvents>` lists `EVENT_HORSE_WHISPERING_1`
- Done trigger's `<Events>` list contains all three done events — that's how the popup shows 3 choices

## Standard XML skeleton

### Start trigger
```xml
<EventTriggerInfo>
    <Type>EVENTTRIGGER_<NAME></Type>
    <WorldNewsTexts/>
    <TriggerTexts>
        <TriggerText>
            <Text>TXT_KEY_EVENT_TRIGGER_<NAME>_1</Text>
            <Era>NONE</Era>
        </TriggerText>
    </TriggerTexts>
    <bSinglePlayer>0</bSinglePlayer>
    <iPercentGamesActive>40</iPercentGamesActive>   <!-- 25-45 typical -->
    <iWeight>200</iWeight>                            <!-- 150-300 typical -->
    <!-- ...zeros for unused fields, see Greed... -->
    <OrPreReqs>
        <PrereqTech>TECH_<X></PrereqTech>
    </OrPreReqs>
    <Events>
        <Event>EVENT_<NAME>_1</Event>
    </Events>
    <PrereqEvents/>
    <bPickPlayer>1</bPickPlayer>
    <PythonCanDo></PythonCanDo>                       <!-- T2: canTrigger<Name> -->
</EventTriggerInfo>
```

### Done trigger (chain via PrereqEvents)
```xml
<EventTriggerInfo>
    <Type>EVENTTRIGGER_<NAME>_DONE</Type>
    <WorldNewsTexts>
        <Text>TXT_KEY_EVENTTRIGGER_<NAME>_DONE</Text>
    </WorldNewsTexts>
    <TriggerTexts>
        <TriggerText>
            <Text>TXT_KEY_EVENT_TRIGGER_<NAME>_DONE_1</Text>
            <Era>NONE</Era>
        </TriggerText>
    </TriggerTexts>
    <iPercentGamesActive>100</iPercentGamesActive>
    <iWeight>-1</iWeight>                              <!-- -1 = always fires when prereqs met -->
    <BuildingsRequired>
        <BuildingRequired>BUILDING_<X></BuildingRequired>
    </BuildingsRequired>
    <iNumBuildings>5</iNumBuildings>
    <Events>
        <Event>EVENT_<NAME>_DONE_1</Event>
        <Event>EVENT_<NAME>_DONE_2</Event>
        <Event>EVENT_<NAME>_DONE_3</Event>
    </Events>
    <PrereqEvents>
        <Event>EVENT_<NAME>_1</Event>
    </PrereqEvents>
    <bGlobal>1</bGlobal>
    <PythonCanDo></PythonCanDo>                        <!-- T2: canTrigger<Name>Done -->
</EventTriggerInfo>
```

### Start event (quest log entry)
```xml
<EventInfo>
    <Type>EVENT_<NAME>_1</Type>
    <Description>TXT_KEY_EVENT_<NAME>_1</Description>
    <QuestFailText>TXT_KEY_EVENT_FAIL_<NAME></QuestFailText>
    <bQuest>1</bQuest>
    <!-- ...all reward fields zeroed... -->
    <PythonExpireCheck></PythonExpireCheck>            <!-- optional: expire<Name>1 -->
    <PythonHelp>getHelp<Name>1</PythonHelp>            <!-- optional but recommended -->
    <Button>,Art/Interface/Buttons/Process/Blank.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,8,5</Button>
    <iAIValue>1000</iAIValue>
</EventInfo>
```

### Done event (per reward choice)
```xml
<EventInfo>
    <Type>EVENT_<NAME>_DONE_1</Type>
    <Description>TXT_KEY_EVENT_<NAME>_DONE_1</Description>
    <bQuest>0</bQuest>
    <bGlobal>1</bGlobal>
    <!-- Reward fields - one or more of: -->
    <iGold>100</iGold>
    <iHappy>1</iHappy>
    <iHealth>1</iHealth>
    <iCulture>50</iCulture>
    <UnitClass>UNITCLASS_<X></UnitClass>
    <iNumFreeUnits>1</iNumFreeUnits>
    <BuildingClass>BUILDINGCLASS_<X></BuildingClass>
    <iBuildingChange>1</iBuildingChange>
    <UnitPromotion>PROMOTION_<X></UnitPromotion>
    <ClearEvents>
        <EventChance>
            <Event>EVENT_<NAME>_1</Event>
            <iEventChance>100</iEventChance>
        </EventChance>
    </ClearEvents>
    <PythonCallback></PythonCallback>                   <!-- T2: applyEvent<Name>Done1 -->
    <PythonHelp>getHelp<Name>Done1</PythonHelp>
    <Button>,Art/Interface/Buttons/Process/Blank.dds,Art/Interface/Buttons/Beyond_the_Sword_Atlas.dds,8,5</Button>
    <iAIValue>1000</iAIValue>
</EventInfo>
```

## Standard text-key skeleton

```xml
<TEXT>
    <Tag>TXT_KEY_EVENT_TRIGGER_<NAME>_1</Tag>
    <English>The popup body shown when the quest starts. Reference player name as %s1_CivAdjective if needed.</English>
</TEXT>
<TEXT>
    <Tag>TXT_KEY_EVENTTRIGGER_<NAME>_DONE</Tag>
    <English>%s1_CivAdjective has completed the &lt;NAME&gt; quest.</English>
</TEXT>
<TEXT>
    <Tag>TXT_KEY_EVENT_TRIGGER_<NAME>_DONE_1</Tag>
    <English>The popup body shown when the quest completes.</English>
</TEXT>
<TEXT>
    <Tag>TXT_KEY_EVENT_<NAME>_1</Tag>
    <English>Quest Title</English>
</TEXT>
<TEXT>
    <Tag>TXT_KEY_EVENT_<NAME>_QUEST</Tag>
    <English>The objective text shown in the quest log.</English>
</TEXT>
<TEXT>
    <Tag>TXT_KEY_EVENT_FAIL_<NAME></Tag>
    <English>You have failed the &lt;NAME&gt; quest.</English>
</TEXT>
<TEXT>
    <Tag>TXT_KEY_EVENT_<NAME>_DONE_1</Tag>
    <English>Reward choice 1 label</English>
</TEXT>
<TEXT>
    <Tag>TXT_KEY_EVENT_<NAME>_DONE_1_HELP</Tag>
    <English>Reward choice 1 tooltip explanation</English>
</TEXT>
```

## Standard Python callback skeleton (T2 only)

```python
######## <NAME> ###########

def getHelp<Name>1(argsList):
    iEvent = argsList[0]
    kTriggeredData = argsList[1]
    return localText.getText("TXT_KEY_EVENT_<NAME>_QUEST", ())

def canTrigger<Name>(argsList):
    kTriggeredData = argsList[0]
    player = gc.getPlayer(kTriggeredData.ePlayer)
    # ...your gating logic here...
    return true

def canTrigger<Name>Done(argsList):
    kTriggeredData = argsList[0]
    player = gc.getPlayer(kTriggeredData.ePlayer)
    # ...your completion-check logic here...
    return true

def applyEvent<Name>Done1(argsList):
    iEvent = argsList[0]
    kTriggeredData = argsList[1]
    player = gc.getPlayer(kTriggeredData.ePlayer)
    # ...optional custom reward effects beyond what XML can express...
    return 1

def expire<Name>1(argsList):
    iEvent = argsList[0]
    kTriggeredData = argsList[1]
    # Return true if the quest should be cancelled (e.g. prereqs gone)
    return false
```

## Where to insert new entries

- `CIV4EventTriggerInfos.xml`: Insert before the closing `</EventTriggerInfos>` tag. Group new quests with a `<!-- DowagerMod new quests -->` comment block.
- `CIV4EventInfos.xml`: Insert before the closing `</EventInfos>` tag. Same comment grouping.
- `CIV4GameText_Events_BTS.xml`: Insert before the closing `</Civ4GameText>` tag. Same comment grouping.
- `CvRandomEventInterface.py`: Insert at the bottom of the file, before any final code. Each quest gets its own `######## <NAME> ###########` block.

## Validation

After authoring a quest, run from the worktree root:
```powershell
python tools\quests\validate_quest_chains.py
python tools\quests\validate_quest_type_refs.py
python tools\quests\smoke_quest_callbacks.py
.\tools\test_gate.ps1
```

All four must pass before committing.

**The `validate_quest_type_refs.py` check is critical** — it catches the most common authoring bug: referencing a TYPE that looks plausible (e.g. `BUILDINGCLASS_TEMPLE`, `BONUS_SALT`, `UNITCLASS_GREAT_PROPHET`) but doesn't exist in vanilla BtS XML. `test_gate.ps1` does NOT catch these because the schema only checks structure, not value. The game catches them at load time with errors like "Tag: X in Info class was incorrect" — by then the mod won't load.

### Common naming gotchas

| Wrong | Right |
|-------|-------|
| `UNITCLASS_GREAT_PROPHET` / `_MERCHANT` / `_ARTIST` etc. | `UNITCLASS_PROPHET` / `_MERCHANT` / `_ARTIST` (no `GREAT_`). Only `UNITCLASS_GREAT_GENERAL` and `UNITCLASS_GREAT_SPY` use the prefix. |
| `UNITCLASS_WORK_BOAT` | `UNITCLASS_WORKBOAT` (no underscore) |
| `UNITCLASS_SWORDMAN` | `UNITCLASS_SWORDSMAN` |
| `BUILDINGCLASS_MONUMENT` | `BUILDINGCLASS_OBELISK` |
| `BUILDINGCLASS_TEMPLE` / `_MONASTERY` / `_CATHEDRAL` | These don't exist generically. Either use a per-religion class (`BUILDINGCLASS_CHRISTIAN_TEMPLE` etc.) or use `<bStateReligion>1</bStateReligion>` with empty `<BuildingsRequired/>` |
| `BONUS_SALT` | Doesn't exist in vanilla BtS. Use `BONUS_INCENSE` or similar luxury. |

When grants free Great People as a reward, use `<FreeSpecialistCounts>` with `SPECIALIST_GREAT_PRIEST` / `_MERCHANT` / `_ARTIST` / `_SCIENTIST` / `_ENGINEER` / `_GENERAL` / `_SPY` — these settle the GP as a permanent specialist. The `SPECIALIST_GREAT_*` form exists; the `UNITCLASS_GREAT_*` form mostly does not.
