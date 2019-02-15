{% trans -%}
================
I2P at BSidesNYC
================
{%- endtrans %}

.. meta::
    :author: sadie, str4d
    :date: 2018-02-12
    :category: meetups
    :excerpt: {% trans %}Trip report about the I2P meetup at BSidesNYC.{% endtrans %}

Sadie and str4d attended BSidesNYC on Saturday January 20th. Thank you to the
BSides Team for setting such a great conference!

Aside from a few talks, we mostly worked on several goals that we had set for
the day during the afternoon in the common area at John Jay College.

Our most pressing task was writing the high-level roadmap for 2018, following
the discussions at 34C3. This has `now been posted`_ - go check it out! We also
picked up some communication threads that were put aside over the holiday period
around our nascent Vulnerability Response Process, and getting it into
"production use".

.. _`now been posted`: {{ url_for('blog_post', slug='2018/02/11/high-level-roadmap') }}

The biggest and most tedious task was working on the information architecture
for the new I2P website. We have a new logo and front page which was designed
for us by the team at `Ura Design`_, but have been blocked on figuring out how
to organise content navigation to create a more user-friendly onboarding
experience. We finished an initial draft of this, and are now working with Ura
to finalize it, before beginning work on the remaining design work.

.. _`Ura Design`: https://ura.design

Finally, we discussed ideas for engagement and outreach this year. We agreed it
would be a good idea to create specific donation tiers, with our existing
stickers at the lower level, and other rewards for larger donations. Potential
reward ideas include:

- More sticker variants (e.g. tesselating sticker)
- T-shirts printed with our new logo
- Other kinds of merch (hoodies, scarves)
- Extension idea: Raspberry Pis in custom 3D-printed cases, pre-loaded with I2P!
  This would require ironing out things like:

  - Having sufficient randomness at boot for generating key material.
  - Ensuring the hardware can handle sufficient network traffic to be a useful
    network participant (older Pis had restricted network interface speeds).
  - Actually making them!

This meetup was a trial run for an idea that we discussed at 34C3: having more
informal I2P-focused meetups throughout the year. And it worked out well! If you
are interested in helping to organise a future meetup, please get in touch with
us. This year I2P developers and community members are attending FOSDEM, HOPE,
Citizen Lab, and BSidesTO, and likely other events - so we will need lots of new
stickers!
