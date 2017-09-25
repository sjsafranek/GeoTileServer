#!/usr/bin/perl 

=comment

[Modules]
cpan -i Geo::StreetAddress::US
cpan -i Data::Dumper::Simple
cpan -i Text::CSV::Separator
cpan -i Text::CSV


=cut


use warnings;
use strict;
use Geo::StreetAddress::US;
use FileHandle;
use Data::Dumper::Simple;
use Text::CSV::Separator qw(get_separator);
use Text::CSV;

my $csv = $ARGV[0];
my $out = $ARGV[1];

my $csvfh = FileHandle->new( "$csv", "r" )
	|| die "Cannot open CSV file $csv for reading: $!\n";

my $outfh = FileHandle->new( "$out", "w" )
	|| die "Cannot open CSV file $out for writing: $!\n";

my $sep = &get_csv_seperator($csv);

my $csvf = Text::CSV->new(
	{ binary => 1, sep_char => $sep, quote_space => 0, auto_diag => 2 } )
	|| die "Cannot use CSV: "
	. Text::CSV->error_diag();    # We die on errors, and put out a message.

my $hdr_ref = $csvf->getline($csvfh);
$csvf->column_names($hdr_ref);
$csvf->combine(@$hdr_ref);
my $header = $csvf->string();

my $out_header = "$header${sep}Residence_Addresses_HouseNumber${sep}Residence_Addresses_PrefixDirection${sep}Residence_Addresses_StreetName${sep}Residence_Addresses_Designator${sep}Residence_Addresses_SuffixDirection${sep}Residence_Addresses_ApartmentType${sep}Residence_Addresses_ApartmentNum\n";

print $outfh $out_header;

while ( my $csvline = $csvf->getline_hr($csvfh) ) {

	#Street Address  City    State   Zip Code
	my $street_address = &trim( $csvline->{'Residence_Addresses_AddressLine'} );
	my $city           = &trim( $csvline->{'Residence_Addresses_City'} );
	my $state          = &trim( $csvline->{'Residence_Addresses_State'} );
	my $zip_code       = &trim( $csvline->{'Residence_Addresses_Zip'} );

	my $addr_string = "$street_address $city, $state $zip_code";

	print "$addr_string\n";

	my $spec = Geo::StreetAddress::US->parse_address($addr_string);

	my $ret_str_num    = '';
	my $ret_str_prefix = '';
	my $ret_str_name   = '';
	my $ret_str_type   = '';
	my $ret_str_suffix = '';
	my $ret_apt_type   = '';
	my $ret_apt_num    = '';
	my $ret_city       = '';
	my $ret_state      = '';
	my $ret_zip        = '';

	$ret_str_num    = $spec->{'number'} if defined $spec->{'number'};
	$ret_str_prefix = $spec->{'prefix'} if defined $spec->{'prefix'};
	$ret_str_name   = $spec->{'street'} if defined $spec->{'street'};
	$ret_str_type   = $spec->{'type'}   if defined $spec->{'type'};
	$ret_str_suffix = $spec->{'suffix'} if defined $spec->{'suffix'};
	$ret_apt_type   = $spec->{'sec_unit_type'}
		if defined $spec->{'sec_unit_type'};
	$ret_apt_num = $spec->{'sec_unit_num'} if defined $spec->{'sec_unit_num'};
	$ret_city    = $spec->{'city'}         if defined $spec->{'city'};
	$ret_state   = $spec->{'state'}        if defined $spec->{'state'};
	$ret_zip     = $spec->{'zip'}          if defined $spec->{'zip'};

	#print "$ret_str_num\n";
	#print "$ret_str_name\n";
	#print "$ret_str_type\n";
	#print "$ret_str_suffix\n";
	#print "$ret_apt_type\n";
	#print "$ret_apt_num\n";
	#print "$ret_city\n";
	#print "$ret_state\n";
	#print "$ret_zip\n";
	#print "\n\n";
	$csvf->combine( @$csvline{@$hdr_ref} );
	my $outline = $csvf->string();
	print $outfh "$outline${sep}$ret_str_num${sep}$ret_str_prefix${sep}$ret_str_name${sep}$ret_str_type${sep}$ret_str_suffix${sep}$ret_apt_type${sep}$ret_apt_num\n";
}

sub trim {
	my $string = shift;
	if ( defined $string ) {
		$string =~ s/^\s+//;
		$string =~ s/\s+$//;
		$string =~ s/^\t+//g;
		$string =~ s/\t$//g;
		$string =~ s/^\n//;
		$string =~ s/\n$//;
		$string =~ s/^\r//;
		$string =~ s/\r$//;
		$string =~ s/"//g;
		$string =~ s/\$//g;
		$string =~ s/^\.00$/0/g;

		# This has to be the last substitution for proper spacing.
		$string =~ s/\s{2,}/ /g;
	}
	return $string;
}

sub get_csv_seperator {
	my $csv_path  = shift;
	my @char_list = get_separator( path => $csv_path );
	my $separator = '';

	if (@char_list) {
		if ( @char_list == 1 ) {

			# successful detection of a single separator.
			$separator = $char_list[0];
		}
		else {

			# Multiple separators.
			print "Multiple CSV candidate characters found: "
				. join( ',', @char_list )
				. "\n Please examine the input file.\n";
			die;
		}
	}
	else {

		# no candidate passed the tests
		print
			"No CSV separator candidates found. Please examine the input file.\n";
		die;
	}
	return $separator;
}


