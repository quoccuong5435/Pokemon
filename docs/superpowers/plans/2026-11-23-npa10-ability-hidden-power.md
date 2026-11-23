# NPA 1.0 Ability, Hidden Ability và Hidden Power cho Pokemon mới: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 285 hero mới có ability thật theo PokeAPI, Hidden Ability cho con thường, và mỗi dạng cuối có Hidden Power riêng theo vai trò.

**Architecture:** Mỗi phần là một module trong `tools/v412/` nhận chuỗi script JASS và trả chuỗi mới, như `ability_rw.py` và `hidden_ability.py`; mọi anchor phải tìm thấy đúng 1 lần, nếu không `ValueError`. Dữ liệu PokeAPI nạp một lần vào JSON. `build_npa10.build_data` gọi các module theo thứ tự. Không thêm item.

**Tech Stack:** Python 3.11 (`python -X utf8 -I`), pytest, JASS kiểm bằng pjass, PokeAPI qua `curl`.

**Spec:** `docs/superpowers/specs/2026-11-23-npa10-ability-hidden-power-design.md` (doc duyệt: https://claude.ai/artifact/SBCQ4SSn7xjkgLkeMQfWxa)

## Global Constraints

- Chữ trong game bằng tiếng Anh; tài liệu và patch note tiếng Việt.
- Không tạo item mới; mở khóa bằng nút "+" (ability `A8xx`).
- Thứ tự `Ab_Want` giữ nguyên: `-abtest` > Mega > form > Hidden Ability đã mở > mặc định loài.
- JASS: không đặt tên biến `code`; hàm khai báo trước chỗ gọi; khối dữ liệu lớn chia hàm tối đa 340 dòng, chạy bằng `ExecuteFunc`; id hero bắt đầu bằng chữ in hoa.
- Chạy Python bằng `python -X utf8 -I`. Code có dấu `\` ghi bằng công cụ Write, không dùng heredoc.
- `tools/v412/` không nằm trong git. Trước khi sửa một file, chép vào `out/backup_<task>/`. Không commit trừ khi người dùng yêu cầu.
- Một agent khác (có thể Gemini) cũng sửa `form_assets.py`, `form_expansion.py`, `build_npa10.py` và build bản 1.0. Trước khi sửa: kiểm mtime và diff với bản sao lưu.
- Build ra `out/*.w3x` bằng `python tools/v412/build_npa10.py --out out/<tên>.w3x --overwrite`. Không thay `New Pokemon Arena 1.0.w3x` khi chưa có OK của người dùng.
- Test: `python -X utf8 -I -m pytest tests/<file> -q`. Số liệu cân bằng lấy từ code, không làm tròn.

## Review Focus

1. Dạng form thiếu dữ liệu PokeAPI: build in danh sách rõ ràng và test chỉ chấp nhận đúng danh sách đã duyệt, không rơi lặng lẽ về Normal / Pressure.
2. Tên ability khác chính tả giữa PokeAPI và map ("quark-drive", "surge-surfer", "own-tempo"): phải khớp, không rơi về ability theo hệ.
3. Người chơi số 11 (slot cuối) sau khi đổi hệ số quest key 64 thành 256: khóa không đè lên người chơi khác.
4. Cùng một hero đổi dạng (Mega, Gigantamax hết giờ, về dạng gốc): ô quest thuộc dạng nào thì ở lại dạng đó, không rò sang dạng khác.
5. 18 Legend caster / striker / drain bắt đầu có hiệu ứng: không nhân đôi với +30% chỉ số và không đụng hiệu ứng tank của 7 con đã có.

---

### Task 0: Fixture dùng chung cho test script build

**Files:**
- Modify: `tests/conftest.py`
- Test: `tests/test_npa_fixture.py`

**Interfaces:**
- Produces: fixture `npa_data` (scope session) trả `dict` với khóa `script: str` (xuống dòng LF), `files: dict[str, bytes]`, `opt_stats: dict`. Dùng `build_npa10.build_data(optimize_assets=False, dev_mode=False)`; mất khoảng 55 giây một lần.

- [ ] **Step 1: Viết test** `test_fixture_has_script`: `assert "function PAX_Leg_QKey" in npa_data["script"]` và `assert npa_data["opt_stats"]["form_models"] == 105`.
- [ ] **Step 2: Chạy, kỳ vọng FAIL** (fixture chưa có): `python -X utf8 -I -m pytest tests/test_npa_fixture.py -q`.
- [ ] **Step 3: Thêm fixture `npa_data`** vào `tests/conftest.py`; thêm `tools` và `tools/v412` vào `sys.path` như `tests/test_new_pokemon_arena.py`; bỏ qua (skip) nếu thiếu `build_npa10.BASE_MAP`.
- [ ] **Step 4: Chạy, kỳ vọng PASS.**

---

### Task 1: Dữ liệu PokeAPI cho 105 dạng form, 44 Mega cũ và 205 con Gen 1-4

Mega cũ cần chỉ số để Task 8 chia vai trò: `fetch_forms.py` cũng tải slug dựng từ `Mega_Name` trong script (`Mega Charizard X` thành `charizard-mega-x`; Primal thành `<loài>-primal`); tên nào không dựng được slug thì vào `form_pokemon_missing.json` như dạng thiếu.

**Files:**
- Create: `tools/pokeapi/fetch_forms.py`, `tools/v412/form_pokeapi.py`
- Output: `tools/pokeapi/form_pokemon.json`, `tools/pokeapi/form_pokemon_missing.json`
- Test: `tests/test_form_pokeapi.py`

**Interfaces:**
- `form_pokemon.json`: `{slug: {"dex": int, "types": [str], "abilities": [str], "hidden": str | None, "stats": [hp, atk, def, spa, spd, spe]}}`. `abilities` chỉ gồm ability thường theo thứ tự slot; ability ẩn nằm riêng ở `hidden`.
- `form_pokeapi.pokemon(slug: str) -> dict | None`, `form_pokeapi.by_dex(dex: int) -> dict | None` (bản gốc của loài), `form_pokeapi.missing() -> list[str]` (khóa form không có trên PokeAPI, đọc từ `form_pokemon_missing.json`).

- [ ] **Step 1: Viết test** trong `tests/test_form_pokeapi.py`:
  `test_aegislash_blade`: `pokemon("aegislash-blade")["types"] == ["steel", "ghost"]`;
  `test_every_form_key_present_or_listed_missing`: `set(form_assets.load_form_assets(pack_files=False)[1]) == set(present) | set(missing())` và hai tập rời nhau;
  `test_g14_entries_have_hidden_flag`: với mọi `dex` trong `gen14_pokedex.json`, `by_dex(dex)` không phải `None` và có khóa `"hidden"`;
  `test_hidden_not_in_abilities`: không bản ghi nào có `hidden` nằm trong `abilities`;
  `test_old_mega_has_stats`: `pokemon("charizard-mega-x")["stats"][1] == 130` (Attack).
- [ ] **Step 2: Chạy, kỳ vọng FAIL** (module và file chưa có).
- [ ] **Step 3: Viết `tools/pokeapi/fetch_forms.py`** theo mẫu `fetch_size.py`: `curl` qua `subprocess`, thử lại 4 lần, cache ở `analysis/pokeapi_cache_meta/form__<slug>.json`, khóa tra là khóa form (`aegislash-blade`) hoặc slug theo dex của `gen14_pokedex.json`. Trả `Not Found` thì ghi khóa vào `form_pokemon_missing.json`. Viết `form_pokeapi.py` đọc hai file JSON.
- [ ] **Step 4: Chạy tải:** `python -X utf8 -I tools/pokeapi/fetch_forms.py`. Kỳ vọng: in số bản ghi và danh sách thiếu.
- [ ] **Step 5: Chạy test, kỳ vọng PASS.**
- [ ] **Step 6 (ĐIỂM DỪNG 1): Ghi danh sách thiếu** vào `docs/form-models/thieu-pokeapi.md` (khóa, tên, vì sao nghi thiếu) rồi báo người dùng duyệt cách xử lý từng con. Không tự điền ability hay hệ cho con thiếu.

---

### Task 2: Bộ đổi tên ability PokeAPI sang số ability của map

**Files:**
- Create: `tools/v412/ability_names.py`
- Test: `tests/test_ability_names.py`

**Interfaces:**
- `ability_index(script: str) -> dict[str, int]`: tên (đúng như `set Ab_Name[i] = "..."`) sang số; tên trùng thì cái đứng sau thắng, như `hidden_ability.ability_table`.
- `slug_to_name(slug: str) -> str`: `"quark-drive"` thành `"Quark Drive"`.
- `first_known(index: dict[str, int], slugs: list[str]) -> int | None`: số ability của slug đầu tiên có trong map, so khớp bỏ qua hoa thường và dấu câu; không có thì `None`.

- [ ] **Step 1: Viết test:** `slug_to_name("quark-drive") == "Quark Drive"`; `first_known({"Surge Surfer": 7}, ["surge-surfer"]) == 7`; `first_known({"Own Tempo": 3}, ["own-tempo"]) == 3`; `first_known({"Pressure": 16}, ["no-such"]) is None`; với `npa_data`: `ability_index(script)["Pressure"] == 16`.
- [ ] **Step 2: Chạy, kỳ vọng FAIL.**
- [ ] **Step 3: Viết module.** Chuẩn hóa hai phía bằng `re.sub(r"[^a-z0-9]", "", s.lower())`.
- [ ] **Step 4: Chạy, kỳ vọng PASS.**

---

### Task 3: Sửa hệ và ability giữ chỗ của 52 form hero và 28 Mega

**Files:**
- Modify: `tools/v412/form_assets.py` (`load_form_assets`, nơi tạo `m_info["types"]`), `tools/v412/form_expansion.py` (đoạn tạo dữ liệu `PF..` gần `ab_id = TYPE_FALLBACK_AB.get(...)` và đoạn Mega `Ab_MegaAb`)
- Test: `tests/test_form_data_fix.py`

**Interfaces:**
- Consumes: `form_pokeapi.pokemon`, `form_pokeapi.missing`, `ability_names.ability_index`, `ability_names.first_known`.
- Produces: `form_expansion.patch_all(...)` trả `stats` có thêm khóa `"ability_fallback": list[str]` (id hero hoặc khóa Mega không tìm thấy ability trong map). Khi `form_pokeapi.pokemon(key)` có dữ liệu: `m_info["types"]` lấy từ đó thay cho `t` rỗng của cây.

- [ ] **Step 1: Viết test** (dùng `npa_data`, đọc `SaveInteger(Ab_HT, 'PF..', 53 / 54 / 0, n)` bằng regex như `scratchpad/new_hero_audit.py`):
  `test_pf_types_match_pokeapi`: với mọi `PF` có dữ liệu, loại 53 và 54 bằng loại PokeAPI (chỉ số theo bảng `TYPE_IDX`, cộng 1);
  `test_no_placeholder_pair`: không `PF` hay `hF` nào đồng thời Normal và Pressure trừ khi PokeAPI nói vậy;
  `test_default_ability_is_first_known`: ability mặc định của mỗi `PF` bằng `first_known(index, abilities)` hoặc nằm trong `stats["ability_fallback"]`;
  `test_mega_ab_megaab_matches_pokeapi`: `Ab_MegaAb[44..71]` tương tự;
  `test_only_approved_forms_fall_back`: tập form thiếu dữ liệu bằng đúng `form_pokeapi.missing()` (Review Focus 1).
- [ ] **Step 2: Chạy, kỳ vọng FAIL** (hiện 52 con đều Normal và Pressure).
- [ ] **Step 3: Sửa `form_assets.py`:** nếu cây không có `t` thì lấy từ `form_pokeapi.pokemon(key)["types"]`.
- [ ] **Step 4: Sửa `form_expansion.py`:** `ab_id` của `PF` và `ab_idx` của Mega = `first_known(ability_index(script), data["abilities"])`; không có thì giữ `TYPE_FALLBACK_AB`, thêm vào `ability_fallback` và in một dòng `[form_expansion] WARNING ... <danh sách>`. Mega chỉ có một ability.
- [ ] **Step 5: Chạy test, kỳ vọng PASS.** Rồi `python tools/v412/build_npa10.py --dry-run`, kỳ vọng `PJASS rc=0`.

---

### Task 4: Ability thật cho 205 con Gen 1-4

**Files:**
- Modify: `tools/v412/gen14_expansion.py` (hàm `_resolve_ability(sp, ab_map)` và chỗ tạo `ab_map` cùng với `move_map`)
- Test: `tests/test_g14_abilities.py`

**Interfaces:**
- `_resolve_ability(sp: dict, ab_index: dict[str, int]) -> int`: dùng `form_pokeapi.by_dex(sp["dex"])["abilities"]` (không gồm ability ẩn) qua `ability_names.first_known`; không có thì `TYPE_FALLBACK_AB`. `ab_index` = `ability_names.ability_index(script)`.

- [ ] **Step 1: Viết test:** `test_spearow_is_keen_eye` (hero `EG00`, `Ab_HT 0` bằng `index["Keen Eye"]`); `test_no_type_fallback_when_ability_exists`: với mọi con Gen 1-4 mà `first_known(...)` không phải `None`, ability mặc định đúng bằng đó.
- [ ] **Step 2: Chạy, kỳ vọng FAIL** (hiện hằng `AB_RW_*` không khớp tên nên rơi về theo hệ).
- [ ] **Step 3: Sửa hàm và nơi gọi.** Bỏ `ab_map` dựng từ hằng `AB_`.
- [ ] **Step 4: Chạy test, kỳ vọng PASS;** chạy lại `tests/test_new_pokemon_arena.py` để chắc không hỏng chỗ khác.

---

### Task 5: Ability cho 4 Paradox mới

**Files:**
- Modify: `tools/v412/form_expansion.py` (`patch_all`, thêm một lần `_once` lên hàm `Ab_Want`)
- Test: `tests/test_form_data_fix.py`

**Interfaces:**
- Sau khi sửa, `Ab_Want` thêm nhánh: `formId == 22` trả `AB_PROTOSYNTHESIS` (Great Tusk); `formId == 20 or 21 or 23` trả `AB_QUARKDRIVE` (Iron Bundle, Iron Hands, Iron Treads). Anchor: `    elseif formId >= 17 and formId <= 19 then\n        return AB_QUARKDRIVE\n    endif`.

- [ ] **Step 1: Viết test** `test_new_paradox_have_ability`: thân hàm `Ab_Want` trong `npa_data["script"]` chứa `formId == 22` kèm `AB_PROTOSYNTHESIS` và `formId == 20` kèm `AB_QUARKDRIVE`.
- [ ] **Step 2: Chạy, kỳ vọng FAIL.**
- [ ] **Step 3: Thêm patch.** Chạy test, kỳ vọng PASS.

---

### Task 6: Hidden Ability cho Gen 1-4 và hero form

**Files:**
- Create: `tools/v412/hidden_ability_new.py`
- Modify: `tools/v412/build_npa10.py` (gọi sau Form Expansion, trước `form_roster`)
- Test: `tests/test_hidden_ability_new.py`

**Interfaces:**
- `collect_entries(script: str, hero_ids: dict[str, str]) -> dict[str, str]`: `hero_ids` là `{id hero: ability ẩn dạng slug}` (Gen 1-4 từ `by_dex(...)["hidden"]`, hero form từ `pokemon(key)["hidden"]`); trả `{id hero: tên ability trong map}` chỉ cho tên có trong `ability_index`.
- `patch(script: str, entries: dict[str, str]) -> str`: thêm hàm `HiddenAb_InitNew` và gọi nó ở cuối `AbilityPatch_Init`. Với mỗi hero ghi `SaveStr(AbilityPatch_HT, 'ID', 1, "Tên")`, khóa 2 là mô tả tiếng Anh lấy từ `ability_rw_text.RW_TEXT`, và `SaveInteger(AbilityPatch_HT, 'ID', 3, số)` chỉ khi ability đó có code (cách kiểm như `hidden_ability.ability_table`: hằng `AB_` được dùng ở nơi khác).

- [ ] **Step 1: Viết test:** `EG00` (Spearow, ẩn Sniper) có khóa 1 bằng `"Sniper"` nếu `Sniper` có trong map; mọi hero có khóa 3 thì tên của nó nằm trong `ability_index`; không hero Mega hay Gigantamax nào có mục mới.
- [ ] **Step 2: Chạy, kỳ vọng FAIL.** Step 3: Viết module, nối vào build. Step 4: Chạy test, kỳ vọng PASS và `PJASS rc=0`.

---

### Task 7: Khóa quest 256 và ô riêng cho mỗi dạng cuối

**Files:**
- Create: `tools/v412/hidden_power.py` (phần slot)
- Modify: `tools/v412/form_expansion.py` (`Form_QuestIdx` và `PAX_Leg_Count`), `tools/v412/build_npa10.py`
- Test: `tests/test_hidden_power_slots.py`

**Interfaces:**
- `FIRST_SLOT = 59`.
- `assign_slots(final_keys: list[str]) -> dict[str, int]`: gán 59, 60, ... theo thứ tự đưa vào; `ValueError` nếu vượt 255. `final_keys` có dạng `mega:<chỉ số>`, `gmax:<id skin hG..>`, `form:<formId>`, `type:<id hero PF cuối>`.
- JASS sinh ra: `Form_FinalSlot(u: unit) -> integer` (kiểm theo đúng thứ tự `Form_IsFinalHP`: Mega, form, Gigantamax đang hoạt động, loại hero cuối) và `Form_QuestIdx` trả `Form_FinalSlot(u)` thay cho hằng 58 khi không phải Legend. `PAX_Leg_Count()` trả `FIRST_SLOT + số dạng cuối - 1`. `PAX_Leg_QKey` trả `1000 + pid * 256 + idx`.

- [ ] **Step 1: Viết test:** `test_slots_unique_and_in_range` (150 khóa mẫu, mọi ô trong 59..255, không trùng); `test_qkey_never_collides`: mô phỏng `1000 + pid*256 + idx` cho `pid` 0..11 và `idx` 0..255 không trùng nhau (Review Focus 3); `test_slot_belongs_to_form_not_hero`: hai khóa `mega:0` và `gmax:hG01` của cùng hero gốc có ô khác nhau (Review Focus 4); `test_script_uses_256` và `test_form_questidx_calls_finalslot` trên `npa_data["script"]`; Legend giữ idx 1..57.
- [ ] **Step 2: Chạy, kỳ vọng FAIL.**
- [ ] **Step 3: Viết `assign_slots` và sinh JASS;** sửa `PAX_Leg_QKey` bằng một lần `_once`. Nguồn danh sách dạng cuối: số Mega (`Mega_N`), `GMAX_BASES`, `PARADOX_SLOTS`, `final_hp_hero_ids` trong `form_expansion.py`.
- [ ] **Step 4: Chạy test, kỳ vọng PASS;** `-quest` và lệnh mở khóa tất cả (`PAX_Leg_UnlockCmd`) duyệt tới `PAX_Leg_Count()` nên phải phủ ô mới.

---

### Task 8: Vai trò và hiệu ứng thức tỉnh

**Files:**
- Modify: `tools/v412/hidden_power.py`, `tools/v412/build_npa10.py`
- Test: `tests/test_hidden_power_roles.py`

**Interfaces:**
- `role_for(stats: list[int], main: str) -> str`: `stats = [hp, atk, def, spa, spd, spe]`, `main` là `"str"` hoặc `"int"`; trả `"tank"` nếu `(def + spd) / 2 >= 105`, ngược lại `"striker"` nếu `main == "str"`, ngược lại `"caster"`. Drain không bao giờ do hàm này trả.
- `LEGEND_ROLES: dict[int, str]` cho idx 33..57 lấy từ `legend_expansion_data.NEW_LEGENDS` (7 tank, 11 caster, 5 striker, 2 drain).
- `slot_roles: dict[int, str]` dựng trong `build_npa10.py`: với mỗi khóa của `assign_slots`, lấy khóa PokeAPI tương ứng (Mega mới: khóa trong `new_megas`; Mega cũ: slug dựng từ `Mega_Name`; Gigantamax: `GMAX_BASES[i][0]`; Paradox: khóa trong `PARADOX_SLOTS`; hero form cuối: khóa trong `copy_move_pairs`), rồi `role_for(stats, "str" nếu atk >= spa, ngược lại "int")`; hợp với `LEGEND_ROLES`.
- `patch(script: str, slot_roles: dict[int, str]) -> str`. JASS thêm: `PAX_Role_Of(idx: integer) -> integer` (1 tank, 2 caster, 3 striker, 4 drain, 0 không có); `PAX_RoleOutMult(src: unit, atk: boolean, skill: boolean) -> real`, nhân vào `m` ngay sau dòng `set m = m * PAX_LightBallDamageMult(src, atk or skill)`; hút máu drain trong `PAX_Leg_OnHit`; `PAX_Leg_ModifyIncoming` thay danh sách cứng `idx == 33 or idx == 34 ...` bằng `PAX_Role_Of(idx) == 1`. Mọi hiệu ứng chỉ chạy khi `PAX_Leg_Awakened(unit)`.
- Số (spec): tank nhân sát thương nhận 0.85; caster nhân 1.15 khi `skill`; striker nhân 1.12 khi `atk or skill`; drain nhân 1.12 và hồi 12% sát thương chiêu gây ra.
- Biểu tượng: 8 ability mới nhân bản từ `AFHL` / `AFHP` bằng `_copy_slk_row` và `_copy_ini_section` (như `form_expansion.py`): `AFL1..AFL4` (khóa) và `AFA1..AFA4` (đã thức tỉnh), tên "Hidden Power: <Vai trò>"; `PAX_Leg_Sync` dùng chúng thay cho `AFHL` / `AFHP` theo vai trò.

- [ ] **Step 1: Viết test:** `role_for([60,100,60,50,60,80], "str") == "striker"`; `role_for([70,50,130,50,100,40], "int") == "tank"` (bulk 115); `role_for([70,50,60,120,60,80], "int") == "caster"`; `Counter(LEGEND_ROLES.values()) == {"tank": 7, "caster": 11, "striker": 5, "drain": 2}`; trên script: không còn chuỗi `idx == 33 or idx == 34 or idx == 35 or idx == 38`, có `PAX_Role_Of` và `PAX_RoleOutMult`; 18 Legend caster/striker/drain đều có `PAX_Role_Of(idx) != 0` (Review Focus 5); `0.85` chỉ xuất hiện một lần trong `PAX_Leg_ModifyIncoming`.
- [ ] **Step 2: Chạy, kỳ vọng FAIL.** Step 3: Viết `role_for`, `LEGEND_ROLES`, `patch`, 8 ability. Mỗi anchor tìm đúng một lần.
- [ ] **Step 4: Chạy test, kỳ vọng PASS và `PJASS rc=0`.**

---

### Task 9: 38+ ability còn thiếu (ĐIỂM DỪNG 2: người dùng duyệt từng cái)

**Files:**
- Create: `analysis/ability_new_plan.py` (sinh `analysis/ability_new_plan.json`)
- Modify (sau khi được duyệt): `tools/v412/ability_rw_data.json` (thêm vào cuối `rw_order`), `tools/v412/ability_rw_text.py` (`RW_TEXT`), `tools/v412/jass/ability_rw_*.j`, hàm `_hooks` trong `tools/v412/ability_rw.py`
- Test: `tests/test_ability_rw.py` (mở rộng)

**Interfaces:**
- `ability_new_plan.json`: danh sách `{name, slug, used_by: [hero], mechanic: str, group: str}` cho mọi tên ability mà con mới cần nhưng `ability_index` không có (hiện 38 trên 236 con có dữ liệu; tính lại sau Task 1). `group` là nhóm cơ chế giống nhau để dùng chung code.
- Thêm vào cuối `rw_order` để số ability cũ không đổi (`RW_INDEX`, `const_name`, `info_id` giữ nguyên công thức).

- [ ] **Step 1: Sinh `ability_new_plan.json`** và trang duyệt (Claude Docs, ô chọn cho từng ability: Đồng ý / Sửa / Bỏ) với đề xuất hiệu ứng viết cho game này, mỗi ability một dòng riêng.
- [ ] **Step 2 (ĐIỂM DỪNG 2): Chờ người dùng duyệt xong.** Không code ability chưa được duyệt.
- [ ] **Step 3: Viết test** `test_new_abilities_registered`: với mỗi ability đã duyệt có `RW_INDEX[name]`, hằng `AB_RW_<TÊN>`, nút thông tin `info_id`, văn bản tiếng Anh, và `ability_index(script)[name]` khớp `RW_INDEX[name]`. Chạy, kỳ vọng FAIL.
- [ ] **Step 4: Cài đặt theo lô tối đa 10 ability,** mỗi lô chạy lại test và `PJASS`. Cơ chế giống nhau dùng chung hàm JASS.
- [ ] **Step 5: Chạy lại Task 3 và Task 4:** `ability_fallback` chỉ còn các mục người dùng đã chọn bỏ.

---

### Task 10: 4 nút "+" cho 4 Paradox mới (làm cuối, rủi ro cao)

**Files:**
- Modify: `tools/v412/form_expansion.py`
- Test: `tests/test_paradox_unlock.py`

**Interfaces:**
- Giống 28 Mega mới (`unlock_id = A8{52 + i}`): 4 ability hero "+" mới `A880..A883` (nhân bản `AEev`, `hero=1`, `levels=1`), thêm vào `uhab` của hero gốc, ánh xạ trong `PAX_UnlockToCastAb`, ability cast `AF28..AF31`. Hành vi cast: đổi hero sang form Paradox tương ứng bằng `PAX_Form_Apply(u, formId)` (formId 20..23).

- [ ] **Step 1 (khảo sát, ghi kết quả vào đầu file test dưới dạng comment):** đọc `PAX_Form_ItemMatches`, `PAX_Form_ItemIndex`, `PAX_Leg_MegaSlotAb`, `PAX_UnlockToCastAb` và cách 10 Paradox cũ đi từ nút "+" tới `PAX_Form_Apply`; đếm số ô lệnh đang dùng trên 4 hero gốc để chắc không vượt 12 ô (lỗi 4.3c từng sửa).
- [ ] **Step 2: Viết test:** `uhab` của mỗi hero gốc chứa id "+" mới; `PAX_UnlockToCastAb` ánh xạ đúng 4 cặp; không hero nào quá 12 ô.
- [ ] **Step 3: Chạy, kỳ vọng FAIL.** Step 4: Cài đặt theo kết quả khảo sát. Step 5: Chạy test, kỳ vọng PASS, `PJASS rc=0`.

---

### Task 11: Build, kiểm toàn bộ, báo cáo

**Files:**
- Output: `out/npa10_ability_hp.w3x`

- [ ] **Step 1: Chạy toàn bộ test:** `python -X utf8 -I -m pytest tests -q`. Kỳ vọng: không lỗi mới so với trước khi sửa.
- [ ] **Step 2: Build:** `python tools/v412/build_npa10.py --out out/npa10_ability_hp.w3x --overwrite`. Kỳ vọng: `PJASS rc=0`, mọi MDX qua `mdx_check`, `Wrote out/npa10_ability_hp.w3x`.
- [ ] **Step 3: Chạy lại kiểm kê** (`scratchpad/coverage_audit.py` và `new_hero_audit.py` hoặc bản sao trong `analysis/`): kỳ vọng `PF` và `hF` không còn Normal + Pressure giả, `Ab_HT 0` của Gen 1-4 khớp PokeAPI, 4 Paradox có ability.
- [ ] **Step 4: Báo cáo** cho người dùng: số con đã sửa, danh sách ability không thể làm, danh sách cần thử trong game (`-quest` với một Mega và một Gigantamax, `-abtest <tên>`, Ability Patch trên một con Gen 1-4, nút "+" của Iron Treads).
- [ ] **Step 5 (ĐIỂM DỪNG 3): Hỏi người dùng** trước khi thay `New Pokemon Arena 1.0.w3x`; khi được OK, sao lưu bản cũ vào `out/` rồi thay, kiểm `who_holds` (không process nào đang giữ file).
