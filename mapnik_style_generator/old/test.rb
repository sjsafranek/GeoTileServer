require 'mapnik'
require 'gdal-ruby/ogr'
require 'gdal-ruby/osr'


# def getFieldInShapefile(shapefile, field):
#     datasource = ogr.Open(shapefile)
#     layer = datasource.GetLayer(0)
#     layerDefinition = layer.GetLayerDefn()
#     for i in range(layerDefinition.GetFieldCount()):
#         if field == layerDefinition.GetFieldDefn(i).GetName():
#             return True
#     return False

# Get epsg from shapefile
def getProj4FromShapefile(shapefile)
    # open prj file
    shapefile['.shp'] = ''
    shapefile += '.prj'
    # shapefile['.shp'] = '.prj'
    prj_file = shapefile
    prj_file_handler = File.open(prj_file)
    # Import the WKT from the PRJ file
    srs = Gdal::Osr::SpatialReference.new()
    srs.import_from_wkt( prj_file_handler.read )
    # return proj4
    prj_file_handler = nil
    return srs.export_to_proj4
end

#
# def getGeometryTypes(shapefile)
#     ds = Gdal::Ogr.open(shapefile)
#     # puts ds.methods
#     layer = ds.get_layer(0)
#     feature = layer.get_next_feature()
#     geom_types = []
#     while not feature.nil?
#         geom_name = feature.get_geometry_ref.get_geometry_name
#         geom_name.slice! 'MULTI'
#         # puts geom_name
#         geom_types.push(geom_name)
#         feature = layer.get_next_feature()
#     end
#     ds = nil
#     return geom_types.uniq
# end


def main()

    datasource_file = 'data/trimet_cell_towers.shp'
    label = "[FULL_NAME]"
    # datasource_file = 'data/world_merc.shp'
    # label = "[NAME]"

    map = Mapnik::Map.new do |m|

        # Use the Google mercator projection
        m.srs =  Mapnik::Tile::DEFAULT_OUTPUT_PROJECTION

        # Add a layer to the map
        m.layer 'layer' do |layer|

            # Add a style to the layer
            layer.style do |style|

                # Add a rule to the style (this one is a default rule)
                style.rule '[mapnik::geometry_type]=polygon' do |rule|
                    #fill the shapes with polygon symbolizers
                    rule.fill = Mapnik::Color.new('#880000')
                    # Style the polygon outline
                    rule.line do |stroke|
                        stroke.color = Mapnik::Color.new('black')
                        stroke.width = 0.5
                    end
                end

                style.rule '[mapnik::geometry_type]=linestring' do |rule|
                    rule.line do |stroke|
                        stroke.color = Mapnik::Color.new('black')
                        stroke.width = 0.5
                    end
                end

                style.rule '[mapnik::geometry_type]=point' do |rule|

                    # puts Mapnik.constants
                    # symbol = Mapnik::PointSymbolizer.new('black')
                    # symbol = Mapnik::MarkersSymbolizer.new('black')
                    # symbol = Mapnik::MarkersSymbolizer.new('ellipse')
                    # puts symbol.methods

                    # puts rule.symbols.methods
                    # puts rule.__append_symbol__(symbol)


                    # default.symbols.methods.push(symbol)
                    # default.symbols << symbol

                    # rule.text "[FULL_NAME]" do |text|
                    rule.text "[NAME]" do |text|
                        text.label_placement = Mapnik::LABEL_PLACEMENT::POINT_PLACEMENT
                        text.fill = Mapnik::Color.new('black')
                        text.halo_fill = Mapnik::Color.new("#fff")
                        text.halo_radius = 0.85
                        text.size = 9
                        text.allow_overlap = false
                        text.avoid_edges = true
                    end

                    # marker.height =  mapnik.Expression("3")
                    # marker.width =  mapnik.Expression("3")
                    # marker.fill = mapnik.Color('black')
                end

                if '' != label
                    style.rule do |rule|
                        rule.text label do |text|
                            text.label_placement = Mapnik::LABEL_PLACEMENT::POINT_PLACEMENT
                            text.fill = Mapnik::Color.new('black')
                            text.halo_fill = Mapnik::Color.new("#fff")
                            text.halo_radius = 0.85
                            text.size = 9
                            text.allow_overlap = false
                            text.avoid_edges = true
                        end
                    end
                end

            end


            # set the srs of the layer
            projection = getProj4FromShapefile(datasource_file)
            layer.srs = projection

            #specify the datasource for the layer
            layer.datasource = Mapnik::Datasource.create :type => 'shape', :file => datasource_file
        end

    end

    map.zoom_to_box(map.layers.first.envelope)
    map.render_to_file('my_map.png')
    print map.to_xml()
end


main()
