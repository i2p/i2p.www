========================
The I2P Proposal Process
========================
.. meta::
    :author: str4d
    :created: 2016-04-10
    :thread: http://zzz.i2p/topics/1980
    :lastupdated: 2016-04-10
    :status: Draft

.. contents::


Overview
========

This document describes how to change the I2P specifications, how I2P proposals
work, and the relationship between I2P proposals and the specifications.

This document is adapted from the Tor proposal process [TORSPEC-PROCESS]_, and
much of the content below was originally authored by Nick Mathewson.

This is an informational document.


Motivation
==========

Previously, our process for updating the I2P specifications was relatively
informal: we'd make a proposal on the development forum and discuss the changes,
then we would reach consensus and patch the specification with draft changes
(not necessarily in that order), and finally we would implement the changes.

This had a few problems.

First, even at its most efficient, the old process would often have the
spec out of sync with the code.  The worst cases were those where
implementation was deferred: the spec and code could stay out of sync for
versions at a time.

Second, it was hard to participate in discussion, since it was not always clear
which portions of the discussion thread were part of the proposal, or which
changes to the spec had been implemented.  The development forums are also only
accessible inside I2P, meaning that proposals could only be viewed by people who
use I2P.

Third, it was very easy to forget about some proposals because they would get
buried several pages back in the forum thread list.


How to change the specs now
===========================

First, somebody writes a proposal document.  It should describe the change that
should be made in detail, and give some idea of how to implement it.  Once it's
fleshed out enough, it becomes a proposal.

Like an RFC, every proposal gets a number.  Unlike RFCs, proposals can change
over time and keep the same number, until they are finally accepted or rejected.
The history for each proposal will be stored in the I2P website repository.

Once a proposal is in the repository, we should discuss it on the corresponding
thread and improve it until we've reached consensus that it's a good idea, and
that it's detailed enough to implement.  When this happens, we implement the
proposal and incorporate it into the specifications.  Thus, the specs remain the
canonical documentation for the I2P protocol: no proposal is ever the canonical
documentation for an implemented feature.

(This process is pretty similar to the Python Enhancement Process, with the
major exception that I2P proposals get re-integrated into the specs after
implementation, whereas PEPs *become* the new spec.)


Small changes
-------------

It's still okay to make small changes directly to the spec if the code can be
written more or less immediately, or cosmetic changes if no code change is
required.  This document reflects the current developers' *intent*, not a
permanent promise to always use this process in the future: we reserve the right
to get really excited and run off and implement something in a
caffeine-or-M&M-fueled all-night hacking session.


How new proposals get added
===========================

To submit a proposal, post it on the development forum [DEV-FORUM-PROPOSAL]_ or
enter a ticket with the proposal attached [TRAC-PROPOSAL]_.

Once an idea has been proposed, a properly formatted (see below) draft exists,
and rough consensus within the active development community exists that this
idea warrants consideration, the proposal editors will officially add the
proposal.

The current proposal editors are zzz and str4d.


What should go in a proposal
============================

Every proposal should have a header containing these fields::

  :author:
  :created:
  :thread:
  :lastupdated:
  :status:

- The ``thread`` field should be a link to the development forum thread where
  this proposal was originally posted, or to a new thread created for discussing
  this proposal.
- The ``lastupdated`` field should initially be equal to the ``created`` field,
  and should be updated whenever the proposal is changed.

These fields should be set when necessary::

  :supercedes:
  :supercededby:

- The ``supercedes`` field is a comma-separated list of all the proposals that
  this proposal replaces. Those proposals should be Rejected and have their
  ``supercededby`` field set to the number of this proposal.

These fields are optional but recommended::

  :target:
  :implementedin:

- The ``target`` field should describe which version the proposal is hoped to be
  implemented in (if it's Open or Accepted).
- The ``implementedin`` field should describe which version the proposal was
  implemented in (if it's Finished or Closed).

The body of the proposal should start with an Overview section explaining what
the proposal's about, what it does, and about what state it's in.

After the Overview, the proposal becomes more free-form.  Depending on its
length and complexity, the proposal can break into sections as appropriate, or
follow a short discursive format.  Every proposal should contain at least the
following information before it is Accepted, though the information does not
need to be in sections with these names.

Motivation
    What problem is the proposal trying to solve?  Why does this problem matter?
    If several approaches are possible, why take this one?

Design
    A high-level view of what the new or modified features are, how the new or
    modified features work, how they interoperate with each other, and how they
    interact with the rest of I2P.  This is the main body of the proposal.  Some
    proposals will start out with only a Motivation and a Design, and wait for a
    specification until the Design seems approximately right.

Security implications
    What effects the proposed changes might have on anonymity, how well
    understood these effects are, and so on.

Specification
    A detailed description of what needs to be added to the I2P specifications
    in order to implement the proposal.  This should be in about as much detail
    as the specifications will eventually contain: it should be possible for
    independent programmers to write mutually compatible implementations of the
    proposal based on its specifications.

Compatibility
    Will versions of I2P that follow the proposal be compatible with versions
    that do not?  If so, how will compatibility be achieved?  Generally, we try
    to not drop compatibility if at all possible; we haven't made a "flag day"
    change since March 2008, and we don't want to do another one.

Implementation
    If the proposal will be tricky to implement in I2P's current architecture,
    the document can contain some discussion of how to go about making it work.
    Actual patches should go on public monotone branches, or be uploaded to
    Trac.

Performance and scalability notes
    If the feature will have an effect on performance (in RAM, CPU, bandwidth)
    or scalability, there should be some analysis on how significant this effect
    will be, so that we can avoid really expensive performance regressions, and
    so we can avoid wasting time on insignificant gains.

References
    If the proposal refers to outside documents, these should be listed.


Proposal status
===============

Open
    A proposal under discussion.

Accepted
    The proposal is complete, and we intend to implement it. After this point,
    substantive changes to the proposal should be avoided, and regarded as a
    sign of the process having failed somewhere.

Finished
    The proposal has been accepted and implemented.  After this point, the
    proposal should not be changed.

Closed
    The proposal has been accepted, implemented, and merged into the main
    specification documents.  The proposal should not be changed after this
    point.

Rejected
    We're not going to implement the feature as described here, though we might
    do some other version.  See comments in the document for details.  The
    proposal should not be changed after this point; to bring up some other
    version of the idea, write a new proposal.

Draft
    This isn't a complete proposal yet; there are definite missing pieces.
    Please don't add any new proposals with this status; put them in the "ideas"
    sub-directory instead.

Needs-Revision
    The idea for the proposal is a good one, but the proposal as it stands has
    serious problems that keep it from being accepted. See comments in the
    document for details.

Dead
    The proposal hasn't been touched in a long time, and it doesn't look like
    anybody is going to complete it soon.  It can become "Open" again if it gets
    a new proponent.

Needs-Research
    There are research problems that need to be solved before it's clear whether
    the proposal is a good idea.

Meta
    This is not a proposal, but a document about proposals.

Reserve
    This proposal is not something we're currently planning to implement, but we
    might want to resurrect it some day if we decide to do something like what
    it proposes.

Informational
    This proposal is the last word on what it's doing. It isn't going to turn
    into a spec unless somebody copy-and-pastes it into a new spec for a new
    subsystem.

The editors maintain the correct status of proposals, based on rough consensus
and their own discretion.


Proposal numbering
==================

Numbers 000-099 are reserved for special and meta-proposals.  100 and up are
used for actual proposals.  Numbers aren't recycled.


References
==========

.. [DEV-FORUM-PROPOSAL]
    http://{{ i2pconv('zzz.i2p') }}/topics/new?forum_id=7-big-topics-ideas-proposals-and-discussion

.. [TORSPEC-PROCESS]
    https://gitweb.torproject.org/torspec.git/tree/proposals/001-process.txt

.. [TRAC-PROPOSAL]
    http://{{ i2pconv('trac.i2p2.i2p') }}/newticket?summary=New%20proposal:%20&type=enhancement&milestone=n/a&component=www/i2p&keywords=review-needed
