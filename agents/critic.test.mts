import {test} from 'node:test';
import assert from 'node:assert/strict';
import {review} from './critic.mts';
const evidence=[{id:'e1',content_sha256:'a'.repeat(64),provenance:{mode:'demo'}}];
test('accept known reference',()=>assert.equal(review({evidence,report:{claims:[{text:'test',evidence_ids:['e1']}]}}).approved,true));
test('reject invented citation',()=>assert.equal(review({evidence,report:{claims:[{text:'test',evidence_ids:['unknown']}]}}).approved,false));
test('reject invalid hash',()=>assert.equal(review({evidence:[{...evidence[0],content_sha256:'bad'}],report:{claims:[{text:'x',evidence_ids:['e1']}]}}).approved,false));
