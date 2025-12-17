# Suggested Schema.org Classes for Generation

This document provides recommendations for additional Schema.org classes to implement in the synthetic RDF generator, organized by category and use case.

## 🎯 High Priority (Already Mentioned in Roadmap)

### 1. **Product** ⭐⭐⭐
**Why:** Essential for e-commerce scenarios, naturally links with Orders, Organizations, and Reviews.

**Key Properties:**
- `name`, `description`, `sku`, `gtin`, `mpn`
- `brand`, `manufacturer`, `category`
- `offers` (price, availability, seller)
- `aggregateRating`, `review`
- `image`, `additionalProperty`
- `weight`, `depth`, `height`, `width`

**Use Cases:**
- Link products to orders (orderedItems)
- Create product catalogs for organizations
- Generate product reviews and ratings
- E-commerce testing and benchmarking

---

### 2. **Event** ⭐⭐⭐
**Why:** Common in many domains (conferences, concerts, sports, webinars), links to Organizations and Places.

**Key Properties:**
- `name`, `description`, `eventStatus`
- `startDate`, `endDate`, `duration`
- `location` (Place or PostalAddress)
- `organizer`, `performer`, `sponsor`
- `offers` (tickets), `maximumAttendeeCapacity`
- `eventAttendanceMode` (online, offline, mixed)

**Use Cases:**
- Event management systems
- Calendar applications
- Conference/meeting scheduling
- Cultural and entertainment events

---

### 3. **Place** ⭐⭐⭐
**Why:** Fundamental for location-based data, used by many other types (Organization, Event, LocalBusiness).

**Key Properties:**
- `name`, `description`, `address`
- `geo` (latitude, longitude)
- `containedInPlace`, `containsPlace`
- `openingHoursSpecification`
- `telephone`, `url`
- `photo`, `image`

**Use Cases:**
- Geographic information systems
- Location-based services
- Mapping applications
- Tourism and travel

---

## 🏪 E-Commerce & Business

### 4. **Offer** ⭐⭐
**Why:** Links Products to Organizations, essential for e-commerce price/availability data.

**Key Properties:**
- `price`, `priceCurrency`, `priceValidUntil`
- `availability`, `itemCondition`
- `seller` (Organization), `eligibleRegion`
- `url`, `validFrom`, `validThrough`
- `priceSpecification` (unit pricing)

**Use Cases:**
- Price comparison sites
- E-commerce platforms
- Marketplace applications
- Inventory management

---

### 5. **Review** / **Rating** ⭐⭐
**Why:** Adds credibility and social proof, links to Products, Organizations, Events, Services.

**Key Properties:**
- `author` (Person), `datePublished`
- `reviewBody`, `reviewRating` (ratingValue, bestRating, worstRating)
- `itemReviewed` (Product, Organization, etc.)
- `publisher` (Organization)

**Use Cases:**
- Review platforms
- E-commerce sites
- Service directories
- Social proof systems

---

### 6. **Invoice** ⭐⭐
**Why:** Financial documents that link Orders, Organizations, and People.

**Key Properties:**
- `invoiceNumber`, `billingPeriod`
- `totalPaymentDue`, `paymentDueDate`
- `accountId`, `paymentStatus`
- `provider` (Organization), `customer` (Person/Organization)
- `referencesOrder` (Order)
- `paymentMethod`

**Use Cases:**
- Accounting systems
- Billing applications
- Financial reporting
- Payment processing

---

## 🏢 Business Specializations

### 7. **LocalBusiness** ⭐⭐
**Why:** Very common Schema.org type, specialization of Organization with location-specific properties.

**Key Properties:**
- Inherits all Organization properties
- `priceRange`, `currenciesAccepted`
- `paymentAccepted`, `openingHours`
- `geo`, `areaServed`
- `hasMap` (URL to map)

**Use Cases:**
- Business directories
- Local search engines
- Restaurant/hotel booking
- Service location finders

---

### 8. **Restaurant** ⭐⭐
**Why:** Popular specialization of LocalBusiness, rich with specific properties.

**Key Properties:**
- Inherits LocalBusiness properties
- `servesCuisine`, `menu`
- `acceptsReservations`, `hasMenu`
- `starRating` (aggregateRating)

**Use Cases:**
- Restaurant discovery apps
- Food delivery platforms
- Reservation systems
- Review sites

---

### 9. **Hotel** ⭐⭐
**Why:** Travel/hospitality industry, links to Places and Organizations.

**Key Properties:**
- Inherits LocalBusiness properties
- `checkinTime`, `checkoutTime`
- `numberOfRooms`, `petsAllowed`
- `starRating`, `amenityFeature`
- `priceRange`

**Use Cases:**
- Hotel booking platforms
- Travel websites
- Hospitality management
- Tourism applications

---

## 📚 Content & Media

### 10. **Article** ⭐⭐
**Why:** News, blog posts, and content management systems.

**Key Properties:**
- `headline`, `articleBody`, `articleSection`
- `author` (Person/Organization), `publisher`
- `datePublished`, `dateModified`
- `wordCount`, `keywords`
- `image`, `video`

**Use Cases:**
- Content management systems
- News aggregators
- Blog platforms
- Publishing systems

---

### 11. **Book** ⭐⭐
**Why:** Library systems, bookstores, educational content.

**Key Properties:**
- `name`, `isbn`, `bookFormat`
- `author` (Person), `publisher` (Organization)
- `numberOfPages`, `datePublished`
- `illustrator`, `translator`
- `aggregateRating`, `review`

**Use Cases:**
- Library catalogs
- Bookstore websites
- Educational platforms
- Reading applications

---

### 12. **Movie** / **MovieSeries** ⭐
**Why:** Entertainment industry, media catalogs.

**Key Properties:**
- `name`, `description`, `datePublished`
- `director`, `actor`, `productionCompany`
- `duration`, `contentRating`
- `aggregateRating`, `trailer`
- `genre`, `keywords`

**Use Cases:**
- Streaming platforms
- Movie databases
- Entertainment websites
- Media catalogs

---

### 13. **VideoObject** ⭐
**Why:** Video content on the web (YouTube, Vimeo, etc.).

**Key Properties:**
- `name`, `description`, `uploadDate`
- `duration`, `contentUrl`, `embedUrl`
- `thumbnailUrl`, `transcript`
- `publisher`, `creator`

**Use Cases:**
- Video platforms
- Media libraries
- Educational content
- Marketing materials

---

## 🎓 Education

### 14. **Course** ⭐⭐
**Why:** Educational platforms, online learning, university systems.

**Key Properties:**
- `name`, `description`, `courseCode`
- `provider` (Organization), `instructor` (Person)
- `coursePrerequisites`, `educationalCredentialAwarded`
- `timeRequired`, `teaches`
- `aggregateRating`, `review`

**Use Cases:**
- Learning management systems
- University catalogs
- Online course platforms
- Educational directories

---

### 15. **EducationalOrganization** ⭐
**Why:** Schools, universities, training centers (specialization of Organization).

**Key Properties:**
- Inherits Organization properties
- `alumni` (Person), `department`
- `award`, `hasCredential`

**Use Cases:**
- School directories
- Alumni networks
- Educational databases
- Training centers

---

## 💼 Employment

### 16. **JobPosting** ⭐⭐
**Why:** Job boards, recruitment platforms, HR systems.

**Key Properties:**
- `title`, `description`, `datePosted`
- `employmentType`, `baseSalary`
- `hiringOrganization` (Organization)
- `jobLocation` (Place), `workHours`
- `qualifications`, `skills`
- `validThrough`

**Use Cases:**
- Job boards
- Recruitment platforms
- HR systems
- Career websites

---

## 🍳 Food & Recipes

### 17. **Recipe** ⭐
**Why:** Cooking websites, food blogs, meal planning apps.

**Key Properties:**
- `name`, `description`, `recipeCategory`
- `recipeIngredient`, `recipeInstructions`
- `prepTime`, `cookTime`, `totalTime`
- `recipeYield`, `nutrition`
- `author` (Person), `image`
- `aggregateRating`

**Use Cases:**
- Recipe websites
- Meal planning apps
- Cooking blogs
- Food platforms

---

## 🚗 Automotive

### 18. **Vehicle** ⭐
**Why:** Car dealerships, automotive marketplaces, rental services.

**Key Properties:**
- `name`, `description`, `vehicleIdentificationNumber` (VIN)
- `brand`, `model`, `productionDate`
- `vehicleConfiguration`, `numberOfDoors`
- `fuelType`, `mileageFromOdometer`
- `offers` (price), `seller` (Organization)

**Use Cases:**
- Car dealership websites
- Automotive marketplaces
- Vehicle rental services
- Fleet management

---

## 💻 Technology

### 19. **SoftwareApplication** ⭐⭐
**Why:** App stores, software catalogs, tech platforms.

**Key Properties:**
- `name`, `description`, `applicationCategory`
- `operatingSystem`, `softwareVersion`
- `offers` (price), `aggregateRating`
- `screenshot`, `downloadUrl`
- `author` (Organization), `publisher`

**Use Cases:**
- App stores
- Software directories
- Developer platforms
- Software marketplaces

---

## 🏥 Healthcare

### 20. **MedicalEntity** / **Hospital** ⭐
**Why:** Healthcare systems, medical directories, health platforms.

**Key Properties:**
- `name`, `description`, `medicalSpecialty`
- `address`, `telephone`, `url`
- `priceRange`, `acceptsInsurance`
- `openingHours`

**Use Cases:**
- Medical directories
- Healthcare platforms
- Hospital websites
- Health information systems

---

## 🎨 Creative Works

### 21. **CreativeWork** (Base Class) ⭐
**Why:** Abstract base for many content types (Article, Book, Movie, etc.).

**Key Properties:**
- `name`, `description`, `creator`
- `dateCreated`, `datePublished`
- `copyrightHolder`, `license`
- `genre`, `keywords`
- `aggregateRating`

**Use Cases:**
- Content management
- Digital libraries
- Creative portfolios
- Media archives

---

## 📊 Data Relationships

### 22. **Dataset** ⭐
**Why:** Data catalogs, research data, open data platforms.

**Key Properties:**
- `name`, `description`, `keywords`
- `creator`, `publisher`, `datePublished`
- `license`, `distribution`
- `temporalCoverage`, `spatialCoverage`
- `measurementTechnique`

**Use Cases:**
- Data catalogs
- Research platforms
- Open data portals
- Scientific databases

---

## 🎯 Implementation Priority Recommendations

### Phase 1 (Next Steps)
1. **Product** - Essential for e-commerce, links to existing Order type
2. **Place** - Fundamental location type, used by many others
3. **Event** - Common use case, good for calendar systems

### Phase 2 (High Value)
4. **Offer** - Links Products to Organizations
5. **Review/Rating** - Adds social proof to Products/Organizations
6. **LocalBusiness** - Very common Schema.org type
7. **Course** - Educational platforms are popular

### Phase 3 (Specialized Domains)
8. **JobPosting** - Employment/HR systems
9. **Restaurant** - Popular LocalBusiness specialization
10. **Article** - Content management systems
11. **Invoice** - Financial document linking
12. **Book** - Library/bookstore systems

### Phase 4 (Niche Use Cases)
- Hotel, Movie, VideoObject, Recipe, Vehicle, SoftwareApplication, etc.

---

## 🔗 Relationship Opportunities

When implementing new types, consider how they link to existing types:

- **Product** → links to: Order (orderedItems), Organization (seller), Review
- **Event** → links to: Organization (organizer), Place (location), Person (attendee)
- **Place** → links to: Organization (address), Event (location), LocalBusiness
- **Review** → links to: Product, Organization, Person (author)
- **Offer** → links to: Product, Organization (seller)
- **JobPosting** → links to: Organization (hiringOrganization), Place (jobLocation)
- **Course** → links to: Organization (provider), Person (instructor)

---

## 📝 Notes

- All new providers should inherit from `BaseSchemaOrgProvider` for code reuse
- Create corresponding SHACL shapes for validation
- Consider adding to `generate_linked_data.py` for relationship generation
- Maintain consistency with existing property naming conventions
- Use Faker's built-in providers where possible (company, address, etc.)

---

**Last Updated:** Based on current project structure and Schema.org vocabulary (v14.0+)


