'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {ReviewDrafts}=require('../../static/drafts.js');

test('switching plates does not attach one reports notes to another',()=>{
 const drafts=new ReviewDrafts();
 assert.equal(drafts.select('report-a'),'');
 drafts.setNotes('Ask Sam about the handling delay on plate A.');
 assert.equal(drafts.select('report-b'),'');
 drafts.setNotes('Plate B used another control lot.');
 assert.equal(drafts.select('report-a'),'Ask Sam about the handling delay on plate A.');
 assert.equal(drafts.select('report-b'),'Plate B used another control lot.');
});
test('reinspection retains notes and explicit import can replace them',()=>{
 const drafts=new ReviewDrafts();drafts.select('report-a');drafts.setNotes('Current draft');
 assert.equal(drafts.select('report-a'),'Current draft');
 drafts.setNotes('Notes from the explicitly opened review');
 assert.equal(drafts.select('report-a'),'Notes from the explicitly opened review');
});
test('invalid note updates do not destroy existing text',()=>{
 const drafts=new ReviewDrafts();drafts.select('report-a');drafts.setNotes('Keep this');
 assert.throws(()=>drafts.setNotes(null));assert.throws(()=>drafts.setNotes('x'.repeat(10001)));
 assert.equal(drafts.select('report-a'),'Keep this');
 assert.throws(()=>new ReviewDrafts().setNotes('No report yet'));
});
