## 1. Memory Store: Status Updates

- [x] 1.1 Implement `MemoryStore.update_status(memory_id, status, valid_until=None)` that mutates the existing row's status/valid_until/updated_at in place and returns the updated `Memory`, and verify a unit test confirms the row's id, type, subject, relation, and value are unchanged while status/valid_until/updated_at reflect the update
- [x] 1.2 Verify updating a nonexistent memory id raises a clear error, with a unit test

## 2. Memory Resolver

- [x] 2.1 Define `ResolverAction` (DUPLICATE / SUPERSEDE / INDEPENDENT) and a `ResolverDecision` Pydantic schema (action, `superseded_memory_id: int | None`, required when action is SUPERSEDE or DUPLICATE), and verify a unit test rejects a SUPERSEDE decision missing `superseded_memory_id`
- [x] 2.2 Write the resolver classification prompt (given the new candidate's relation+value and the existing same-subject+relation ACTIVE memories with their ids/values, classify DUPLICATE/SUPERSEDE/INDEPENDENT) and implement `MemoryResolver.classify(candidate_memory, existing_related_memories) -> ResolverDecision` using the LLM provider (verified live against Groq on career-change/independent-preference/duplicate cases)
- [x] 2.3 Implement `MemoryResolver.resolve(candidate_memory, store) -> Memory | None`: looks up existing ACTIVE memories with the same subject+relation; if none found, returns the candidate as a new independent fact without calling the LLM; if found, calls `classify` and applies the result (DUPLICATE → returns None and creates nothing; SUPERSEDE → calls `store.update_status` on the matched memory and returns a new memory with `supersedes_memory_id` set; INDEPENDENT → returns a new memory with no supersede link)
- [x] 2.4 Implement the uncertainty check: if `candidate_memory.confidence` is below the certainty threshold constant, `resolve` SHALL skip classification entirely and return the candidate as a new memory with status UNCERTAIN, and verify a unit test confirms no existing ACTIVE memory is touched
- [x] 2.5 Verify with mocked LLM responses: duplicate restatement produces no new record; a career-change candidate with an existing same-relation ACTIVE memory produces a SUPERSEDE (old memory's status becomes SUPERSEDED, new memory is ACTIVE with `supersedes_memory_id` set); a same-relation "also like Python" candidate against an existing "likes Kotlin" memory produces INDEPENDENT (both remain ACTIVE); a low-confidence hedged candidate produces UNCERTAIN without any classification call

## 3. Wire Resolver into Extraction and Storage

- [x] 3.1 Replace the direct `store.save` call in `extract_and_store` with a resolver-backed path: each SAVE candidate is embedded (as before) and passed through `MemoryResolver.resolve`, and the result (if any) is what gets saved, and verify existing extraction tests still pass with the resolver wired in (duplicate/uncertain cases return no additional row; superseded/independent cases behave as in Task Group 2)
- [x] 3.2 Verify an integration test: given a store already containing an ACTIVE `works_at: Google` memory, running extraction+resolution on "I left Google and joined Microsoft" (mocked LLM extraction + resolver responses) results in Google SUPERSEDED and Microsoft ACTIVE in the store afterward

## 4. Historical Memory Retrieval

- [x] 4.1 Implement `MemoryRetriever.retrieve_historical(message, top_k)` mirroring `retrieve()` but filtering `store.list(status=SUPERSEDED)`, and verify a unit test confirms only SUPERSEDED memories are ever returned, ranked by descending similarity
- [x] 4.2 Verify the bounded result set and empty-result behavior (no SUPERSEDED memories exist) with unit tests

## 5. Historical Context in the Conversation Loop

- [x] 5.1 Extend `build_messages` to accept an optional `historical_memories` list and render it as a section labeled distinctly from `RELEVANT USER MEMORY` (e.g. `RELEVANT HISTORICAL MEMORY`), with prompt instruction that historical entries are past state, not current, and verify a unit test confirms both sections appear correctly labeled when both are non-empty, and the historical section is omitted when empty
- [x] 5.2 Wire `ConversationEngine.handle_message` to call `retriever.retrieve_historical(user_message, top_k=2)` alongside the existing `retrieve()` call and pass both into `build_messages`, and verify a unit test with a mocked LLM confirms historical memories reach the prompt

## 6. End-to-End Verification

- [x] 6.1 Verify live via the real CLI: tell the companion "I work at Google", then "I left Google and joined Microsoft", then ask "Where do I work?" and confirm the answer is Microsoft
- [x] 6.2 In the same live session, ask "Where did I work before Microsoft?" and confirm the answer references Google as past, not current, employment
- [x] 6.3 Verify independent facts still coexist live: tell the companion "I like Kotlin" then "I also like Python", then ask what languages it knows you like, and confirm both are referenced rather than one replacing the other

All 6 task groups verified. Live run confirmed: "Where do I work?" -> Microsoft (current); "Where did I work before Microsoft?" -> Google (correctly framed as past); both Kotlin and Python retained as coexisting preferences.
