from __future__ import (absolute_import, division, print_function,
                    unicode_literals)

from prov.model import ProvDocument, Namespace, Literal, PROV, Identifier, ProvAgent
import datetime
import pydotplus, prov.dot

def example():

    g = ProvDocument()
    # Local namespace
    # Doesnt exist yet so we are creating it
    ap = Namespace('aip', 'https://araport.org/provenance/')
    # Dublin Core
    g.add_namespace("dcterms", "http://purl.org/dc/terms/")
    # FOAF
    g.add_namespace("foaf", "http://xmlns.com/foaf/0.1/")

    # We support multiple generative agents for ADAMA
    # Add: foaf:phone, prov:role
    me = g.agent(ap['matthew_vaughn'], {
        'prov:type': PROV["Person"], 'foaf:givenName': "Matthew Vaughn", 'foaf:mbox': "<mailto:vaughn@tacc.utexas.edu>", 'foaf:phone':"512-867-5309", 'prov:role':"Principal Investigator"
    })
    walter = g.agent(ap['walter_moreira'], {
        'prov:type': PROV["Person"], 'foaf:givenName': "Walter Moreira", 'foaf:mbox': "<mailto:wmoreira@tacc.utexas.edu>", 'prov:role':"Lead Software Developer"
    })

    # Each generative agent can have multiple sponsors
    # Add: address in form of dcterms:Location
    utexas = g.agent(ap['university_of_texas'], {
        'prov:type': PROV["Organization"], 'foaf:givenName': "University of Texas at Austin", 'dcterms:Location': "Austin, TX 78712"
    })

    # Add: uri as foaf:homepage
    araport = g.agent(ap['araport'], {
        'prov:type': PROV["Organization"], 'foaf:givenName': "The Arabidopsis Information Portal", 'foaf:homepage':"https://www.araport.org/"
    })

    # Establish the linkage between authors and their sponsors
    # Note that we can now have multiple sponsors per Person agent
    # Downside is that for every author, one has to enumerate the list of sponsors in the YAML
    # In the full implementation in ADAMA may want to scan for all the 'sponsors'
    # and generate a non-duplicative list
    g.actedOnBehalfOf(walter, utexas)
    g.actedOnBehalfOf(walter, araport)
    g.actedOnBehalfOf(me, utexas)
    g.actedOnBehalfOf(me, araport)

    # ADAMA platform
    # Add: prov.type = prov:SoftwareAgent
    adama_platform = g.agent(ap['adama_platform'], {'prov:type': PROV["SoftwareAgent"], 'dcterms:title': "ADAMA", 'dcterms:description': "Araport Data and Microservices API", 'dcterms:language':"en-US", 'dcterms:identifier':"https://api.araport.org/community/v0.3/", 'dcterms:updated': "2015-04-17T09:44:56" })
    g.wasGeneratedBy(adama_platform, walter)

    # Microservice
    # Add: prov.type = prov:SoftwareAgent
    microservice_name = 'mwvaughn/bar_annotation_v1.0.0'
    adama_microservice = g.agent(ap[microservice_name], {'prov:type': PROV["SoftwareAgent"], 'dcterms:title': "BAR Annotation Service", 'dcterms:description': "Returns annotation from locus ID", 'dcterms:language':"en-US", 'dcterms:identifier':"https://api.araport.org/community/v0.3/mwvaughn/bar_annotation_v1.0.0", 'dcterms:source':"https://github.com/Arabidopsis-Information-Portal/prov-enabled-api-sample" })
    g.wasGeneratedBy(adama_platform, me)

    # No changes
    g.wasGeneratedBy(adama_microservice, me, datetime.datetime.now())
    # The microservice used the platform now
    g.used(adama_microservice, adama_platform, datetime.datetime.now())

    ## Sources

    # Authors. These are also prov:Agent objects
    # Add: prov:role, foaf:phone, foaf:homepage mapping to role, phone, and uri in Sources.yml
    nick = g.agent(ap['nicholas_provart'], {
        'prov:type': PROV["Person"], 'foaf:givenName': "Nicholas Provart", 'foaf:mbox': "provart@utoronta.ca", 'prov:role':"Principal Investigator", 'foaf:phone':"999-999-999", 'foaf:homepage':"http://csb.utoronto.ca/faculty/nicholas-provart/"
    })
    # The service can have additional authors. Here, we describe Asher and his role
    asher = g.agent(ap['asher'], {
        'prov:type': PROV["Person"], 'foaf:givenName': "Asher Pasha", 'prov:role':"Software Developer"
    })

    # Add: dcterms:Location as Sources.yml address
    utoronto = g.agent(ap['university_of_toronto'], {
        'prov:type': PROV["Organization"], 'foaf:givenName': "University of Toronto", 'dcterms:identifier':"http://www.utoronto.ca/", 'dcterms:Location':"123 Main Street, Toronto, Canada"
    })

    # In Sources.yml, both Nick and Asher list U Toronto as one of their sponsors
    # however, Asher does not have all the extended attributes for that sponsor, only its
    # name and uri. The 'utoronto' agent should be a union of the multiple enumerations of
    # the same source, with 'name' being the identifying key. In case of conflict between
    # optional child fields (for instance, conflicting versions of 'uri', ADAMA should
    # raise an exception
    g.actedOnBehalfOf(nick, utoronto)
    g.actedOnBehalfOf(asher, utoronto)

    # Now, the actual BAR resource
    # Add: citiations

    # The resource itself
    datasource1 = g.entity(ap['datasource1'], {'dcterms:title': "BAR Arabidopsis AGI -> Annotation", 'dcterms:description': "Most recent annotation for given AGI", 'dcterms:language':"en-US", 'dcterms:updated':"2015-04-17T09:44:56", 'dcterms:license':"Creative Commons 3.0", 'dcterms:identifier':"http://bar.utoronto.ca/webservices/agiToAnnot.php" })

    # Define citations
    citations = []
    citations.append( g.entity(ap['citation1'], {'dcterms:bibliographicCitation':"An \"Electronic Fluorescent Pictograph\" Browser for Exploring and Analyzing Large-Scale Biological Data Sets. PLOS One. August 8, 2007", 'dcterms:identifier': 'DOI: 10.1371/journal.pone.0000718'} ) )
    citations.append( g.entity(ap['citation2'], {'dcterms:bibliographicCitation':"ePlant and the 3D Data Display Initiative: Integrative Systems Biology on the World Wide Web. PLOS One. January 10, 2011", 'dcterms:identifier': 'DOI: 10.1371/journal.pone.0015237'} ) )

    # The citations result from the existence of the data source,
    # and are thus derived from it
    for cite in citations:
        g.wasDerivedFrom(cite, datasource1)

    # Set up attribution to Nick
    g.wasAttributedTo(datasource1, nick)
    g.wasAttributedTo(datasource1, asher)

    # Nested sources: TAIR
    # Added citations, links sections

    eva = g.agent(ap['eva_huala'], {
        'prov:type': PROV["Person"], 'foaf:givenName': "Eva Huala"
    })

    phoenix = g.agent(ap['phoenix_bioinformatics'], {
        'prov:type': PROV["Organization"], 'foaf:givenName': "Phoenix Bioinformatics", 'dcterms:homepage':"http://phoenixbioinformatics.org/"
    })
    g.actedOnBehalfOf(eva, phoenix)

    # The resource
    datasource2 = g.entity(ap['datasource2'], {'dcterms:title': "TAIR", 'dcterms:description': "The Arabidopsis Information Resource", 'dcterms:language':"en-US", 'dcterms:identifier':"https://www.arabidopsis.org/"})

    # Citations
    citations = []
    citations.append( g.entity(ap['citation3'], {'dcterms:bibliographicCitation':"The Arabidopsis Information Resource (TAIR): improved gene annotation and new tools. Nucleic Acids Research 2011", 'dcterms:identifier':"doi: 10.1093/nar/gkr1090"} ))
    citations.append( g.entity(ap['citation4'], {'dcterms:bibliographicCitation':"The arabidopsis information resource: Making and mining the \"gold standard\" annotated reference plant genome. Berardini et. al. Nucleic Acids Research. Volume 53, Issue 8, pages 474485, August 2015", 'dcterms:identifier': "DOI: 10.1002/dvg.22877"} ))

    for cite in citations:
        g.wasDerivedFrom(cite, datasource2)

    # Include all Authors...
    g.wasAttributedTo(datasource2, eva)

    # No change
    g.wasDerivedFrom(ap['datasource1'], ap['datasource2'])

    # Define actions
    # For all ADAMA mediators, we define a single action: mediate
    action1 = g.activity(ap['query'], datetime.datetime.now())
    # This is a placeholder - for native APIs we will send the action 'generate'
    #action3 = g.activity(ap['generate'], datetime.datetime.now())

    # No change
    response = g.entity(ap['adama_response'])

    # Response is generated by the process_query action
    # Time-stamp it!
    g.wasGeneratedBy(response, action1, datetime.datetime.now())
    # The process_query used the microservice
    g.used(action1, adama_microservice, datetime.datetime.now())
    # The microservice used datasource1
    g.used(adama_microservice, datasource1, datetime.datetime.now())

    pd = open('Sources.provn.txt', 'w')
    pd.write( g.get_provn() )
    pd.close

    # Print prov-json
    pj = open('Sources.json', 'w')
    pj.write( g.serialize() )
    pj.close

    # Write out as a pretty picture
    graph = prov.dot.prov_to_dot(g)
    graph.write_png('Sources.png')

