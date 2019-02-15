{% trans -%}
===========================
High-level Roadmap for 2018
===========================
{%- endtrans %}
.. meta::

    :author: str4d
    :date: 2018-02-11
    :category: roadmap
    :excerpt: {% trans %}2018 will be the year of new protocols, new collaborations, and a more refined focus.{% endtrans %}

{% trans -%}
One of the many things we discussed at 34C3 was what we should focus on for the
coming year. In particular, we wanted a roadmap that was clear about what we
want to ensure we get done, vs what would be really nice to have, and be able to
help onboard newcomers to either category. Here is what we came up with:
{%- endtrans %}

{% trans -%}
Priority: New crypto(graphy!)
-----------------------------
{%- endtrans %}

{% trans -%}
Many of the current primitives and protocols still retain their original designs
from circa 2005, and need improvement. We have had a number of open proposals
for several years with ideas, but forward progress has been slow. We all agreed
that this needs to be our top priority for 2018. The core components are:

- New transport protocols (to replace NTCP and SSU). See Prop111_.
- New onion-encryption protocol for building and using tunnels.
- New NetDB datatypes to enable enhanced Destinations. See Prop123_.
- Upgraded end-to-end protocol (replacing ElGamal).

{%- endtrans %}

.. _Prop111: {{ proposal_url('111') }}
.. _Prop123: {{ proposal_url('123') }}

{% trans -%}
Work on this priority falls into several areas:

- Writing proposals.
- Writing working implementations of them that we can test.
- Reviewing proposals.

{%- endtrans %}

{% trans -%}
We cannot release new protocol specifications across the entire network without
work on all of these areas.
{%- endtrans %}

{% trans -%}
Nice-to-have: Code reuse
------------------------
{%- endtrans %}

{% trans -%}
One of the benefits of starting the above work now, is that over the last few
years there have been independent efforts to create simple protocols and
protocol frameworks that achieve many of the aims we have for our own protocols,
and have gained traction with the wider community. By leveraging this work, we
get a "force multiplier" effect:

- We benefit from protocol designs, security proofs, and code written by others,
  reducing the amount of work we need to do for the same level of
  feature-completeness and security assurances.

- Work we do can be leveraged by other communities, increasing their interest in
  collaborating with us, and thinking about I2P as a whole.

{%- endtrans %}

{% trans -%}
My proposals in particular will be leveraging the `Noise Protocol Framework`_,
and the `SPHINX packet format`_. I have collaborations lined up with several
people outside I2P for these!
{%- endtrans %}

.. _`Noise Protocol Framework`: https://noiseprotocol.org/
.. _`SPHINX packet format`: https://katzenpost.mixnetworks.org/docs/specs/sphinx.html

{% trans -%}
Priority: Clearnet collaboration
--------------------------------
{%- endtrans %}

{% trans -%}
On that topic, we've been slowly building interest over the last six months or
so. Across PETS2017, 34C3, and RWC2018, I've had some very good discussions
about ways in which we can improve collaboration with the wider community. This
is really important to ensure we can garner as much review as possible for new
protocols. The biggest blocker I've seen is the fact that the majority of I2P
development collaboration currently happens inside I2P itself, which
significantly increases the effort required to contribute.
{%- endtrans %}

{% trans -%}
The two priorities in this area are:

- Set up a project-run development forum that is accessible both inside and
  outside I2P.

- Set up mailing lists for review and discussion of proposals (possibly
  connected to the above forum).

{%- endtrans %}

{% trans -%}
Other goals which are classed as nice-to-have:

- Set up a usable git-to-mtn pathway, to enable us to effectively solicit
  clearnet contributions on GitHub while keeping the canonical dev environment
  on Monotone.

- Write a "position paper" that accurately explains I2P to academic audiences,
  and puts it in context with existing literature.

{%- endtrans %}

{% trans -%}
I expect that collaborations with people outside I2P will be done entirely on
GitHub, for minimal friction.
{%- endtrans %}

{% trans -%}
Priority: Preparation for long-lived releases
---------------------------------------------
{%- endtrans %}

{% trans -%}
I2P is now in Debian Sid (their unstable repo) which will stablilise in around a
year and a half, and has also been pulled into the Ubuntu repository for
inclusion in the next LTS release in April. We are going to start having I2P
versions that end up hanging around for years, and we need to ensure we can
handle their presence in the network.
{%- endtrans %}

{% trans -%}
The primary goal here is to roll out as many of the new protocols as we feasibly
can in the next year, to hit the next Debian stable release. For those that
require multi-year rollouts, we should incorporate the forward-compatability
changes as early as we can.
{%- endtrans %}

{% trans -%}
Priority: Pluginization of current apps
---------------------------------------
{%- endtrans %}

{% trans -%}
The Debian model encourages having separate packages for separate components. We
agreed that decoupling the currently-bundled Java applications from the core
Java router would be beneficial for several reasons:

- It codifies the boundary between the applications and the router.

- It should make it easier to get these apps running with non-Java routers.

- It would enable third parties to create "I2P bundles" containing just the
  applications they want.

{%- endtrans %}

{% trans -%}
In combination with the earlier priorities, this moves the main I2P project more
in the direction of e.g. the Linux kernel. We will spend more time focusing on
the network itself, leaving third-party developers to focus on applications that
use the network (something that is significantly easier to do after our work in
the last few years on APIs and libraries).
{%- endtrans %}

{% trans -%}
Nice-to-have: App improvements
------------------------------
{%- endtrans %}

{% trans -%}
There are a bunch of app-level improvements that we want to work on, but do not
currently have the developer time to do so, given our other priorities. This is
an area we would love to see new contributors for! Once the above decoupling is
complete, it will be significantly easier for someone to work on a specific
application independently of the main Java router.
{%- endtrans %}

{% trans -%}
One such application we would love to have help with is I2P Android. We will be
keeping it up-to-date with the core I2P releases, and fixing bugs as we can, but
there is much that could be done to improve the underlying code as well as the
usability.
{%- endtrans %}

{% trans -%}
Priority: Susimail and I2P-Bote stabilisation
---------------------------------------------
{%- endtrans %}

{% trans -%}
Having said that, we do want to work specifically on Susimail and I2P-Bote fixes
in the near term (some of which have landed in 0.9.33). They have had less work
over the last few years than other I2P apps, and so we want to spend some time
bringing their codebases up to par, and making them easier for new contributors
to jump into!
{%- endtrans %}

{% trans -%}
Nice-to-have: Ticket triage
---------------------------
{%- endtrans %}

{% trans -%}
We have a large backlog of tickets in a number of I2P subsystems and apps. As
part of the above stabilisation effort, we would love to clean up some of our
older long-standing issues. More importantly, we want to ensure that our tickets
are correctly organised, so that new contributors can find good tickets to work
on.
{%- endtrans %}

{% trans -%}
Priority: User support
----------------------
{%- endtrans %}

{% trans -%}
One aspect of the above we will be focusing on is keeping in touch with users
who take the time to report issues. Thank you! The smaller we can make the
feedback loop, the quicker we can resolve problems that new users face, and the
more likely it is that they keep participating in the community.
{%- endtrans %}

{% trans -%}
We'd love your help!
--------------------
{%- endtrans %}

{% trans -%}
That all looks very ambitious, and it is! But many of the items above overlap,
and with careful planning we can make a serious dent in them.
{%- endtrans %}

{% trans -%}
If you are interested in helping with any of the goals above, come chat to us!
You can find us on OFTC and Freenode (#i2p-dev), and Twitter (@GetI2P).
{%- endtrans %}
