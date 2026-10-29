'use strict';
// Notes belong to a computed report, not whichever plate happens to load next.
// This is tab memory only, never browser storage or a server-side record.
class ReviewDrafts {
 constructor(){this.notes=new Map();this.active=null;}
 select(reportId){
  if(typeof reportId!=='string'||!reportId)throw Error('A report identifier is required.');
  this.active=reportId;
  return this.notes.get(reportId)||'';
 }
 setNotes(notes){
  if(typeof notes!=='string'||notes.length>10000)throw Error('Notes must be text of at most 10,000 characters.');
  if(!this.active)throw Error('Inspect a report before adding notes.');
  this.notes.set(this.active,notes);
 }
}
if(typeof module!=='undefined'&&module.exports)module.exports={ReviewDrafts};
